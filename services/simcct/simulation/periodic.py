# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# periodic.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'Arvy Salazar <@Xaraox>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.20'
"""periodic.py: 

This module is a helper utility to store the elements in a periodic table with 
all it's atomic number, symbols, names, and atomic weight. 
"""

import enum

import prettytable


class Element(object):
    """Simple element object to store as value in the Periodic Table enum."""
    def __init__(
        self, atomic_num: int, name: str, symbol: str, atomic_mass: float
    ):
        self.atomic_num = atomic_num
        self.name = name
        self.symbol = symbol
        self.atomic_mass = atomic_mass

    def get_full_name(self):
        return '{} ({})'.format(self.name, self.symbol)

    def __str__(self):
        return '{:3.1f}: {:14} | {}'.format(
            self.atomic_num, self.get_full_name(), self.atomic_mass
        )


class PeriodicTable(enum.Enum):
    H = Element(1, 'Hydrogen', 'H', 1.008)
    He = Element(2, 'Helium', 'He', 4.0026)
    Li = Element(3, 'Lithium', 'Li', 6.94)
    Be = Element(4, 'Beryllium', 'Be', 9.0122)
    B = Element(5, 'Boron', 'B', 10.811)
    C = Element(6, 'Carbon', 'C', 12.0115)
    N = Element(7, 'Nitrogen', 'N', 14.0067)
    Mg = Element(12, 'Magnesium', 'Mg', 24.305)
    Al = Element(13, 'Aluminium', 'Al', 26.9815)
    Si = Element(14, 'Silicon', 'Si', 28.085)
    P = Element(15, 'Phosphorous', 'P', 30.9738)
    S = Element(16, 'Sulphur', 'S', 32.065)
    Cl = Element(17, 'Chlorine', 'Cl', 35.45)
    Ar = Element(18, 'Argon', 'Ar', 39.948)
    K = Element(19, 'Potassium', 'K', 39.098)
    Ca = Element(20, 'Calcium', 'Ca', 40.078)
    Sc = Element(21, 'Scandium', 'Sc', 44.956)
    Ti = Element(22, 'Titanium', 'Ti', 47.867)
    V = Element(23, 'Vanadium', 'V', 50.9415)
    Cr = Element(24, 'Chromium', 'Cr', 52.0)
    Mn = Element(25, 'Manganese', 'Mn', 54.938)
    Fe = Element(26, 'Iron', 'Fe', 55.845)
    Co = Element(27, 'Cobalt', 'Co', 58.94)
    Ni = Element(28, 'Nickel', 'Ni', 58.71)
    Cu = Element(29, 'Copper', 'Cu', 63.546)
    Zn = Element(30, 'Zinc', 'Zn', 65.38)
    Ga = Element(31, 'Gallium', 'Ga', 69.723)
    Ge = Element(32, 'Germanium', 'Ge', 72.630)
    As = Element(33, 'Arsenic', 'As', 74.9216)
    Se = Element(34, 'Selenium', 'Se', 78.971)
    Br = Element(35, 'Bromine', 'Br', 79.904)
    Kr = Element(36, 'Krypton', 'Kr', 83.798)
    Rb = Element(37, 'Rubidium', 'Rb', 85.468)
    Sr = Element(38, 'Strontium', 'Sr', 87.62)
    Y = Element(39, 'Yttrium', 'Y', 88.906)
    Zr = Element(40, 'Zirconium', 'Zr', 91.224)
    Nb = Element(41, 'Niobium', 'Nb', 92.9064)
    Mo = Element(42, 'Molybdenum', 'Mo', 95.94)
    Tc = Element(43, 'Technetium', 'Tc', 98.0)
    Ru = Element(44, 'Ruthenium', 'Tu', 101.7)
    Rh = Element(45, 'Rhodium', 'Rh', 102.91)
    Pd = Element(46, 'Palladium', 'Pd', 106.42)
    Ag = Element(47, 'Silver', 'Ag', 107.87)
    Cd = Element(48, 'Cadmium', 'Cd', 112.41)
    In = Element(49, 'Indium', 'In', 114.82)
    Sn = Element(50, 'Tin', 'Sn', 118.71)
    Sb = Element(51, 'Antimony', 'Sb', 121.76)
    Te = Element(52, 'Tellurium', 'Te', 127.60)
    I = Element(53, 'Iodine', 'I', 126.90)
    Xe = Element(54, 'Xenon', 'Xe', 131.29)
    Cs = Element(55, 'Caesium', 'Cs', 132.91)
    Ba = Element(56, 'Barium', 'Ba', 137.33)
    La = Element(57, 'Lanthanum', 'La', 138.91)
    Ce = Element(58, 'Cerium', 'Ce', 140.12)
    Pr = Element(59, 'Praseodymium', 'Pr', 140.91)
    Nd = Element(60, 'Neodymium', 'Nd', 144.24)
    Pm = Element(61, 'Promethium', 'Pm', 145.0)
    Sm = Element(62, 'Samarium', 'Sm', 150.36)
    Eu = Element(63, 'Europium', 'Eu', 151.96)
    Gd = Element(64, 'Gadolinium', 'Gd', 157.25)
    Tb = Element(65, 'Terbium', 'Tb', 158.93)
    Dy = Element(66, 'Dysprosium', 'Dy', 162.50)
    Ho = Element(67, 'Holmium', 'Ho', 164.93)
    Er = Element(68, 'Erbium', 'Er', 167.26)
    Tm = Element(69, 'Thulium', 'Tm', 169.93)
    Yb = Element(70, 'Ytterbium', 'Yb', 173.05)
    Lu = Element(71, 'Lutetium', 'Lu', 174.97)
    Hf = Element(72, 'Hafnium', 'Hf', 178.49)
    Ta = Element(73, 'Tantalum', 'Ta', 180.95)
    W = Element(74, 'Tungsten', 'W', 183.85)
    Re = Element(75, 'Rhenium', 'Re', 186.21)
    Os = Element(76, 'Osmium', 'Os', 190.23)
    Ir = Element(77, 'Iridium', 'Ir', 192.22)
    Pt = Element(78, 'Platinum', 'Pt', 195.08)
    Au = Element(79, 'Gold', 'Au', 196.97)
    Hg = Element(80, 'Mercury', 'Hg', 200.59)
    Tl = Element(81, 'Thallium', 'Tl', 204.38)
    Pb = Element(82, 'Lead', 'Pb', 207.2)
    Bi = Element(83, 'Bismuth', 'Bi', 208.980)
    Po = Element(84, 'Polonium', 'Po', 209.0)
    At = Element(85, 'Astatine', 'At', 210.0)
    Rn = Element(86, 'Radon', 'Rn', 222.0)
    Fr = Element(87, 'Francium', 'Fr', 223.0)
    Ra = Element(88, 'Radium', 'Ra', 226.0)
    Ac = Element(89, 'Actinium', 'Ac', 227.0)
    Th = Element(90, 'Thorium', 'Th', 232.04)
    Pa = Element(91, 'Protactinium', 'Pa', 231.04)
    U = Element(92, 'Uranium', 'U', 238.03)
    Np = Element(93, 'Neptunium', 'Np', 237.0)
    Pu = Element(94, 'Plutonium', 'Pu', 244.0)
    Am = Element(95, 'Americium', 'Am', 243.0)
    Cm = Element(96, 'Curium', 'Cm', 247.0)
    Bk = Element(97, 'Berkelium', 'Bk', 247.0)
    Cf = Element(98, 'Californium', 'Cf', 251.0)
    Es = Element(99, 'Einsteinium', 'Es', 252.0)
    Fm = Element(100, 'Fermium', 'Fm', 257.0)
    Md = Element(101, 'Mendelevium', 'Md', 258.0)
    No = Element(102, 'Nobelium', 'No', 259.0)
    Lr = Element(103, 'Lawrencium', 'Lr', 266.0)
    Rf = Element(104, 'Rutherfordium', 'Rf', 267.0)
    Db = Element(105, 'Dubnium', 'Db', 268.0)
    Sg = Element(106, 'Seaborgium', 'Sg', 269.0)
    Bh = Element(107, 'Bohrium', 'Bh', 270.0)
    Hs = Element(108, 'Hassium', 'Hs', 270.0)
    Mt = Element(109, 'Meitnerium', 'Mt', 278.0)
    Ds = Element(110, 'Darmstadtium', 'Ds', 281.0)
    Rg = Element(111, 'Roentgenium', 'Rg', 282.0)
    Cn = Element(112, 'Copernicium', 'Cn', 285.0)
    Nh = Element(113, 'Nihonium', 'Nh', 286.0)
    Fl = Element(114, 'Flerovium', 'Fl', 289.0)
    Mc = Element(115, 'Moscovium', 'Mc', 290.0)
    Lv = Element(116, 'Livermorium', 'Lv', 293.0)
    Ts = Element(117, 'Tennessinem', 'Ts', 294.0)
    Og = Element(118, 'Oganesson', 'Og', 294.0)


if __name__ == '__main__':
    # USAGE: Run Python periodic.py to see the full Periodic Table printed.
    table = prettytable.PrettyTable(['Atom #', 'Name (Symbol)', 'Atomic Mass'])
    for elem in PeriodicTable:
        table.add_row(
            [
                elem.value.atomic_num,
                elem.value.get_full_name(), elem.value.atomic_mass
            ]
        )
    table.align['Atom #'] = 'c'
    table.align['Name (Symbol)'] = 'l'
    table.align['Atomic Mass'] = 'l'
    print(table)
