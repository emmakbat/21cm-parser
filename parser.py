import csv
import numpy as np

class Measurement:
    '''
    object for holding 21 cm measurement data
    '''

    def __init__(self, coords, coord_to_dist, coord_type, tsys, cal_const=0):
        '''
        inputs: 
        coords: list of tuples of coordinates
        coord_to_dist: dictionary whose keys are coords and whose
        items are [[freqs], [intensities]]
        coord_type: either galactic or azel
        tsys: calibration temperature of system
        '''
        self.coords = coords
        self.coord_to_dist = coord_to_dist
        self.coord_type = coord_type
        self.tsys = tsys
        self.cal_const = cal_const

    def report(self):
        print('21 cm Telescope Measurement')
        print('tsys: ', self.tsys)
        print('Coordinate type: ', self.coord_type)
        print('Coordinates:')
        print(self.coords)

    def get_coords(self):
        return self.coords

    def get_data(self, x, y):
        ''' returns all data at coord as list of list of frequencies
        and list of list of intensities'''
        all_data = self.coord_to_dist[(x, y)]
        freqs = []
        intensities = []
        for dataset in all_data:
            freqs.append(dataset[0])
            intensities.append(dataset[1])
        return freqs, intensities

    def plot(self, coord, now=True):
        '''plots all data at given coordinate'''
        all_data = self.coord_to_dist[coord]
        ax = plt.subplot(111)
        for dataset in all_data:
            ax.plot(dataset[0][8:-8], dataset[1][8:-8])
        if now:
            plt.show()
        return ax

    def calibrate_tsys(self):
        '''subtracts temperate calibration'''
        self.vals = [val - tsys for val in self.vals]

def read_npoint(document, filepath):
    with open(filepath + '/' + document, newline='\n') as doc:
        docreader = csv.reader(doc, delimiter='\t')
        for row in docreader:
            # ignore comments
            if row[0].startswith('*'):
                pass
            else:
                # data starts at n=11
                size = int(np.sqrt(int(row[10])))
                data = np.zeros((size, size))
                row_ind = 0
                for i in range(size):
                    for j in range(size):
                        data[i, j] = float(row[11 + row_ind])
                        row_ind += 1
    return data, size

def read_gal_file(document, filepath):
    '''return freq and intensity data from file
    
    returns measurement object'''
    gal_coord = []
    coord_to_dist = {}
    tsys = 0
    with open(filepath + '/' + document, newline='\n') as doc:
        docreader = csv.reader(doc, delimiter='\t')
        for row in docreader:
            # ignore comments
            if row[0].startswith('* tsys'):
                tsys = int(row[0][9:12])
            elif row[0].startswith('*'):
                pass
            else:
                gal_long = round(float(row[5]))
                gal_lat = round(float(row[6]))
                gal_coord.append((gal_long, gal_lat))

                start_freq = float(row[7])
                freq_increment = float(row[8])
                num_points = int(row[10])

                freqs = []
                intensities = []
                for point in range(11, 11+num_points):
                    freq = start_freq + freq_increment*(point - 11)
                    freqs.append(freq)
                    intensity = float(row[point])
                    intensities.append(intensity-tsys)
                if (gal_long, gal_lat) in coord_to_dist:
                    coord_to_dist[(gal_long, gal_lat)].append([freqs, intensities])
                else:
                    coord_to_dist[(gal_long, gal_lat)] = [[freqs, intensities]]
    return Measurement(gal_coord, coord_to_dist, 'galactic', tsys)

def read_sun_file(document, filepath):
    '''return freq and intensity data from file
    
    returns list of tuples of azel coords which are keys
    into dictionary whose items are [[freqs], [intensities]]'''
    azel_coord = []
    coord_to_dist = {}
    tsys = 0
    cal_const = 0
    with open(filepath + '/' + document, newline='\n') as doc:
            docreader = csv.reader(doc, delimiter='\t')
            for row in docreader:
                # ignore comments
                if row[0].startswith('* tsys'):
                    tsys = int(row[0][9:12])
                    cal_const = float(row[0][20:28])
                elif row[0].startswith('*'):
                    pass
                else:
                    az = round(float(row[5]))
                    el = round(float(row[6]))
                    azel_coord.append((az, el))

                    start_freq = float(row[7])
                    freq_increment = float(row[8])
                    num_points = int(row[10])

                    freqs = []
                    intensities = []
                    for point in range(11, 11+num_points):
                        freq = start_freq + freq_increment*point
                        freqs.append(freq)
                        intensity = float(row[point])
                        intensities.append(intensity-tsys)
                    coord_to_dist[(az, el)] = [[freqs, intensities]]
    return Measurement(azel_coord, coord_to_dist, 'azel', tsys, cal_const)