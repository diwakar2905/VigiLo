# config/migration.py
from config.exceptions import MigrationError
from config.defaults import CURRENT_CONFIG_VERSION
from logs.logger import logger


class ConfigMigrator:
    @staticmethod
    def migrate(config_dict):
        """Runs sequential version migrations on the configuration dictionary in place."""
        version = config_dict.get("version", 0)

        if version > CURRENT_CONFIG_VERSION:
            raise MigrationError(
                f"Configuration version {version} is newer than current supported version {CURRENT_CONFIG_VERSION}."
            )

        while version < CURRENT_CONFIG_VERSION:
            migration_func_name = f"_migrate_v{version}_to_v{version + 1}"
            migration_func = getattr(ConfigMigrator, migration_func_name, None)

            if not migration_func:
                raise MigrationError(
                    f"No migration path defined from v{version} to v{version + 1}."
                )

            logger.info(
                f"Migrating configuration schema from version {version} to {version + 1}..."
            )
            config_dict = migration_func(config_dict)
            version = config_dict.get("version", 0)

        return config_dict

    @staticmethod
    def _migrate_v0_to_v1(config_dict):
        """Migrates legacy configurations (version 0) to version 1."""
        # 1. Update version field
        config_dict["version"] = 1

        # 2. Backport missing core blocks with default structures
        if "telegram" not in config_dict:
            config_dict["telegram"] = {}
        if "security" not in config_dict:
            config_dict["security"] = {}
        if "camera" not in config_dict:
            config_dict["camera"] = {}

        return config_dict

    @staticmethod
    def _migrate_v1_to_v2(config_dict):
        """Migrates version 1 configurations to version 2."""
        # 1. Update version field
        config_dict["version"] = 2

        # 2. Backport missing face_verification config with default structures
        if "face_verification" not in config_dict:
            config_dict["face_verification"] = {
                "enabled": False,
                "threshold": 0.363,
                "reference_embeddings": [],
            }

        return config_dict

    @staticmethod
    def _migrate_v2_to_v3(config_dict):
        """Migrates version 2 configurations to version 3."""
        # 1. Update version field
        config_dict["version"] = 3

        # 2. Backport missing vault config with default structures
        if "vault" not in config_dict:
            config_dict["vault"] = {
                "enabled": True,
                "target_dir": "C:\\VigiLoVault",
                "vault_key": "",
            }

        return config_dict

    @staticmethod
    def _migrate_v3_to_v4(config_dict):
        """Migrates version 3 configurations to version 4."""
        # 1. Update version field
        config_dict["version"] = 4

        # 2. Backport missing whatsapp config with default structures
        if "whatsapp" not in config_dict:
            config_dict["whatsapp"] = {
                "enabled": False,
                "phone_number_id": "",
                "access_token": "",
                "recipient_phone": "",
            }

        return config_dict
