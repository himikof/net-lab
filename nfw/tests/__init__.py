import unittest

if __name__ == "__main__":
    test_loader = unittest.defaultTestLoader.discover('.')
    print test_loader
    test_runner = unittest.TextTestRunner()
    #test_runner.run(test_loader)
