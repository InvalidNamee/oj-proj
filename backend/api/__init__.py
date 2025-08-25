from flask import Blueprint

def register_blueprints(app):
    import os, importlib

    api_dir = os.path.dirname(__file__)
    for fname in os.listdir(api_dir):
        if fname.endswith(".py") and fname != "__init__.py":
            module_name = f"api.{fname[:-3]}"
            module = importlib.import_module(module_name)
            for item_name in dir(module):
                item = getattr(module, item_name)
                if isinstance(item, Blueprint):  # ✅ 只注册真正的 Blueprint
                    app.register_blueprint(item)
