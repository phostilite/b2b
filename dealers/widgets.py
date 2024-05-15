from django import forms

class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None, **kwargs):
        super().__init__(attrs=attrs, **kwargs)
        self.attrs['multiple'] = True

    def value_from_datadict(self, data, files, name):
        if isinstance(files, list):
            return [f for f in files if f is not None]
        else:
            return files.getlist(name)

    def value_omitted_from_data(self, data, files, name):
        return False