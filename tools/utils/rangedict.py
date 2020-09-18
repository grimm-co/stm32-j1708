
class RangeDict(dict):
    def __setitem__(self, key, value):
        if isinstance(key, tuple) and len(key) == 2:
            a, b = key
            key = range(a, b+1)
        if key in self:
            old_key = self.get_key(key)
            assert key == old_key
        super().__setitem__(key, value)

    def __getitem__(self, match_key):
        for key, value in self.items():
            if isinstance(key, range):
                if match_key in key:
                    return value
            elif match_key == key:
                return value
        raise KeyError

    def __len__(self):
        keylen = 0
        for key in self:
            if isinstance(key, range):
                keylen += len(key)
            else:
                keylen += 1

        return keylen

    def __contains__(self, match_key):
        for key, value in self.items():
            if isinstance(key, range):
                if match_key in key:
                    return True
            elif match_key == key:
                return True
        return False

    def get_key(self, match_key):
        # Special function for this object: allow a way to retrieve the key that 
        # matches, useful when determining if a value is in the dict because of 
        # a value or a range
        for key, value in self.items():
            if isinstance(key, range):
                if match_key in key:
                    return key
            elif match_key == key:
                return key

    def min(self):
        cur_min = None
        for key in self:
            if isinstance(key, range):
                key_val = key.start
            else:
                key_val = key

            if not cur_min:
                cur_min = key_val
            elif key_val < cur_min:
                cur_min = key_val
        return cur_min

    def max(self):
        cur_max = None
        for key in self:
            if isinstance(key, range):
                key_val = key.stop - 1
            else:
                key_val = key

            if not cur_max:
                cur_max = key_val
            elif key_val > cur_max:
                cur_max = key_val
        return cur_max


class DefaultRangeDict(RangeDict):
    def __init__(self, default, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._default = default

    def __missing__(self, key):
        return self._default
