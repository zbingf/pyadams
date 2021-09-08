

import numpy as np

class PartFile:

    def __init__(self, file_path):

        self.file_path = file_path

    def read_file(self):

        with open(self.file_path, 'r') as f:
            lines = f.read().split('\n')[1:]

        data = [[value for value in line.split(',') if value] for line in lines if line]

        x_line = []
        y_line = []
        for line in data:
            x_line.append(line[0])
            y_line.append(line[1])

        self.x_line = x_line
        self.y_line = y_line

        return x_line, y_line

    def fit_line(self):

        x_line = self.x_line
        y_line = self.y_line
        
        x_line = [float(value) for value in x_line]
        y_line = [float(value) for value in y_line]

        obj = np.polyfit(x_line, y_line, 3)
        fit_obj = np.poly1d(obj)
        self.fit_obj = fit_obj

    def get_y(self, x):

        return self.fit_obj(x)

class ResistanceFile(PartFile):

    def __init__(self, file_path):
        super().__init__(file_path)
        self.read_file()
        self.titles = self.x_line
        self.values = [float(value) for value in self.y_line]






if __name__ == '__main__':
    pass


    r_obj = ResistanceFile(r'.\resistance\管段局部阻力.csv')
    print(r_obj.titles, r_obj.values)


    c_obj = PartFile(r'.\cell\test.csv')
    c_obj.read_file()
    c_obj.fit_line()
    print(c_obj.get_y([1,2,3]))



