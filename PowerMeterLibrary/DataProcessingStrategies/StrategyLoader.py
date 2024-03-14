import importlib
import pkgutil

class DataProcessingStrategyLoader:
    def __init__(self, package_name, base_class_name):
        self.strategies = []
        self.package_name = package_name
        self.base_class_name = base_class_name
        self.load_strategies()

    def load_strategies(self):
        # Import the package
        package = importlib.import_module(self.package_name)
        # Dynamically import the base class to check against it
        base_module = importlib.import_module(f"{self.package_name}.data_processing_strategy")
        base_class = getattr(base_module, self.base_class_name)
        # Iterate through the modules in the package
        for _, module_name, _ in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            # Import the module
            module = importlib.import_module(module_name)
            # Iterate through attributes of the module
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                # Check if the attribute is a class, it's not the base class,
                # and it is a subclass of the base class
                if isinstance(attribute, type) and attribute is not base_class and issubclass(attribute, base_class):
                    # Instantiate the class and add it to the strategies list
                    self.strategies.append(attribute())

