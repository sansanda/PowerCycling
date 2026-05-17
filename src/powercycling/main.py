from instruments.mocks.electronic_loads import FakeHPElectronicLoad6060B
from instruments.interfaces.interfaces import ElectronicLoadInterface

def depInjection(elI:ElectronicLoadInterface):
    print(elI.mode)

def main():
    el = FakeHPElectronicLoad6060B()
    depInjection(el)


if __name__ == "__main__":
    main()