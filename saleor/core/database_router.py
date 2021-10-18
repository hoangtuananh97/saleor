class AIDatabaseRouter:
    ai_app_labels = ["saleor_ai"]

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.ai_app_labels:
            return "ai_db"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.ai_app_labels:
            return "ai_db"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.ai_app_labels
            or obj2._meta.app_label in self.ai_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.ai_app_labels:
            return db == "ai_db"
        return True
