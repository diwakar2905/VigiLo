# core/event_monitor.py
import time
import win32evtlog
from logs.logger import logger

class EventLogMonitor:
    def __init__(self, event_id=4625, threshold=2, check_interval=0.5, callback=None):
        self.event_id = event_id
        self.threshold = threshold
        self.check_interval = check_interval
        self.callback = callback
        self.server = "localhost"
        self.log_type = "Security"

    def start(self, stop_event):
        """
        Starts the event log monitoring loop. Blocks until stop_event is set.
        """
        logger.info(f"Starting Event Log Monitor (Target EventID: {self.event_id}, Threshold: {self.threshold})")
        
        try:
            handle = win32evtlog.OpenEventLog(self.server, self.log_type)
            
            # Position at the end of the log
            back_flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(handle, back_flags, 0)
            last_record = events[0].RecordNumber if events else 0
            logger.info(f"Event Log Monitor anchored at initial record: {last_record}")
            
            failed_count = 0
            
            while not stop_event.is_set():
                try:
                    # Seek read starting from the last known record
                    flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEEK_READ
                    events = win32evtlog.ReadEventLog(handle, flags, last_record)
                    
                    if not events:
                        time.sleep(self.check_interval)
                        continue
                        
                    for event in events:
                        if event.RecordNumber <= last_record:
                            continue
                            
                        last_record = event.RecordNumber
                        
                        if event.EventID == self.event_id:
                            failed_count += 1
                            logger.warning(f"Security Alert: Failed login attempt detected! Count: {failed_count}")
                            
                            if failed_count >= self.threshold:
                                logger.info(f"Failed login threshold ({self.threshold}) reached. Triggering action.")
                                if self.callback:
                                    try:
                                        self.callback()
                                    except Exception as cb_err:
                                        logger.error(f"Event Log callback error: {cb_err}")
                                failed_count = 0 # Reset count
                                
                    time.sleep(self.check_interval)
                    
                except Exception as loop_err:
                    logger.error(f"Error in Event Log read loop (likely log cleared or wrapped): {loop_err}")
                    time.sleep(2)
                    # Re-open handle and re-anchor to prevent stuck index loops
                    try:
                        handle = win32evtlog.OpenEventLog(self.server, self.log_type)
                        back_flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
                        events = win32evtlog.ReadEventLog(handle, back_flags, 0)
                        last_record = events[0].RecordNumber if events else 0
                        logger.info(f"Event Log Monitor successfully re-anchored at: {last_record}")
                    except Exception as re_err:
                        logger.error(f"Failed to re-anchor event log: {re_err}")
        except Exception as init_err:
            logger.critical(f"Failed to open Windows Security Event Log: {init_err}")
