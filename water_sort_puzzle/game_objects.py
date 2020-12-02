import copy
from functools import wraps
from collections import UserList
from water_sort_puzzle.exceptions import VialCannotAcceptThisException, VialIsFullException


def validate_path(path):
    if path is not None:
        assert isinstance(path, list), 'Path must be list type!'
        for i in path:
            assert isinstance(i, tuple), 'All path members must be tuples!'
            assert len(i) == 2, 'All path tuples must be length of 2!'


class Path(UserList):
    def __init__(self, initlist=None):
        validate_path(initlist)
        super().__init__(initlist)

    def __str__(self):
        if len(self) == 0:
            return super().__str__()

        result = []
        i_prev = None
        for i in self:
            if i_prev != i:
                result.append(f'{i[0] + 1}->{i[1] + 1}')
            i_prev = i
        return ', '.join(result)


class Vial(UserList):

    def __init__(self, max_size, initlist=None):
        check_vial_arguments_meet_requirements(max_size, initlist)

        super().__init__(initlist)
        self.max_size = max_size

    def is_full(self):
        if len(self.data) < self.max_size:
            return False
        else:
            return True

    def is_empty(self):
        if len(self.data) == 0:
            return True
        else:
            return False

    def can_accept(self, item):
        if self.is_empty():
            return True
        if not self.is_full():
            if item == self.data[-1]:
                return True
        return False

    def __raise_exception_if_full(self):
        if self.is_full():
            raise VialIsFullException('Vial is full and cannot accept more items')

    def append(self, item):
        self.__raise_exception_if_full()
        super().append(item)

    def count_unique(self):
        return len(set(self))


def check_vial_arguments_meet_requirements(max_size, initlist):
    assert max_size > 0, 'max_size must be greater than zero!'
    assert isinstance(max_size, int), 'max_size must be integer!'

    if initlist is not None:
        assert len(initlist) <= max_size, 'initlist size cannot be greater than max_size!'


def log_move(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        method_output = method(self, *method_args, **method_kwargs)
        self.path.append(tuple(method_args))
        return method_output
    return _impl


def reset_path(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        method_output = method(self, *method_args, **method_kwargs)
        self.path = Path()
        return method_output
    return _impl


def check_type_list_of_lists(input_list):
    if not isinstance(input_list, list):
        return False
    for i in input_list:
        if not isinstance(i, list):
            return False
    return True


def check_type_list_of_vials(input_list):
    if not isinstance(input_list, list):
        return False
    for i in input_list:
        if not isinstance(i, Vial):
            return False
    return True


def raise_exception_if_not_list_of_lists(input_list):
    if not check_type_list_of_lists(input_list):
        raise TypeError(f'expected list of lists, got {type(input_list)}')


def get_max_internal_list_size(list_of_lists):
    n = 0
    for l in list_of_lists:
        if len(l) > n:
            n = len(l)
    return n


def make_vials_from_lists(input_list):
    raise_exception_if_not_list_of_lists(input_list)
    max_size = get_max_internal_list_size(input_list)
    if max_size < 2:
        max_size = 2
    result = []

    for i in input_list:
        vial = Vial(max_size, i)
        result.append(vial)
    return result


class VialBoard(UserList):

    path = Path()

    @reset_path
    def __init__(self, vial_list):
        if check_type_list_of_lists(vial_list):
            vial_list = make_vials_from_lists(vial_list)

        check_board_arguments_meet_requirements(vial_list)

        super().__init__(vial_list)
        self.init_data = copy.deepcopy(self.data)

    def __str__(self):
        result = ''
        size = self[0].max_size
        for line in range(size-1, -1, -1):
            for vial in self:
                if len(vial) > line:
                    result += f'|{vial[line]:->3}|'
                else:
                    result += f'|---|'
            result += '\n'
        return result

    def can_move(self, donor_index, recipient_index):
        if donor_index == recipient_index:
            return False

        donor_vial = self[donor_index]
        recipient_vial = self[recipient_index]

        if donor_vial.is_empty():
            return False
        elif recipient_vial.can_accept(donor_vial[-1]):
            return True
        return False

    def get_set_of_items(self):
        s = set()
        for vial in self:
            s = s.union(vial)
        return s

    @log_move
    def __make_simple_move(self, donor_index, recipient_index):
        item = self[donor_index].pop()
        self[recipient_index].append(item)

    def move(self, donor_index, recipient_index):
        while self.can_move(donor_index, recipient_index):
            self.__make_simple_move(donor_index, recipient_index)

    @reset_path
    def restart_game(self):
        self.data = copy.deepcopy(self.init_data)

    def solved(self):
        game_items = set()
        for vial in self:
            if not vial.is_empty():
                if vial.count_unique() > 1:
                    return False
                elif vial[0] in game_items:
                    return False
                game_items.add(vial[0])
        return True

    def __get_last_step(self):
        return self.path[-1]

    def __get_last_step_size(self):
        i = 0
        while self.path[-i - 1] == self.__get_last_step():
            i += 1
            if i == len(self.path):
                break
        return i

    def step_back(self):
        n = self.__get_last_step_size()
        for i in range(n):
            step = self.path.pop()
            item = self[step[1]].pop()
            self[step[0]].append(item)


def check_board_arguments_meet_requirements(vial_list):
    assert len(vial_list) > 1, 'VialBoard should contain at least 2 Vials!'
    first_vial = vial_list[0]
    for i in vial_list:
        assert isinstance(i, Vial), 'VialBoard elements all must be instances of Vial class!'
        assert first_vial.max_size == i.max_size


class PlotableVialBoard(VialBoard):
    # defination of colors
    LG = LIGHTGREEN = 'LIGHTGREEN'
    GY = GRAY = 'GRAY'
    OR = ORANGE = 'ORANGE'
    YE = YELLOW = 'YELLOW'
    RE = RED = 'RED'
    PU = PURPLE = 'PURPLE'
    GR = GREEN = 'GREEN'
    PI = PINK = 'PINK'
    BR = BROWN = 'BROWN'
    DG = DARKGREEN = 'DARKGREEN'
    BL = BLUE = 'BLUE'
    LB = LIGHTBLUE = 'SKYBLUE'

    colors = {
        'LIGHTGREEN': '#79DF83',
        'GRAY': '#55585E',
        'ORANGE' : '#E88A45',
        'YELLOW' : '#FDEA68',
        'RED': '#B22923',
        'PURPLE': '#571F86',
        'GREEN': '#74931F',
        'PINK': '#DF5D73',
        'BROWN': '#6A3D11',
        'DARKGREEN': '#20562B',
        'BLUE': '#2920BC',
        'LIGHTBLUE': '#5D9EEA',
    }
    
    def _get_color(self, dict_n2c, n):
        if n in dict_n2c.keys():
            return dict_n2c[n]
        else:
            for i in self.colors.keys():
                if i not in dict_n2c.values():
                    dict_n2c[n] = i
                    return i
            raise 

    def _get_num(dict_c2n, c):
        pass
    def __init__(self, vial_list_color):
        dict_n2c = {}
        dict_c2n = {}

        via_list_num = []
        for l in vial_list:
            temp_list = []
            for c in l:
                