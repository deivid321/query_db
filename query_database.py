import sys
# import getopt
import sqlite3
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.widgets import Slider, Button, RadioButtons
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_, not_


def read_data(conn, values, path, run, luminosity):
    lumisections = []
    properties = [] #16
    rs = None
    for i in range(0, 18):
        properties.append([])

    property_name = ['PATH', 'RUN_NUMBER', 'LUMISECTION', 'ENTRIES', 'X_MEAN', 'X_MEAN_ERROR', 'X_RMS', 'X_RMS_ERROR',
                     'X_UNDERFLOW', 'X_OVERFLOW', 'Y_MEAN', 'Y_MEAN_ERROR', 'Y_RMS', 'Y_RMS_ERROR', 'Y_UNDERFLOW',
                     'Y_OVERFLOW', 'Z_MEAN', 'Z_MEAN_ERROR', 'Z_RMS', 'Z_RMS_ERROR', 'Z_UNDERFLOW', 'Z_OVERFLOW']

    def set_properties(stm):
        rs = conn.execute(stm).fetchall()
        for row in rs:
            lumisections.append(row[2])
            for property in range(0, 18):
                properties[property].append(row[property + 4])

    try:
        if (path and luminosity and run>=0):
            print "QUERY: SELECT * FROM HISTOGRAM_VALUES WHERE LUMISECTION =", luminosity, "AND RUN_NUMBER =", run, "AND PATH =", path
            stm = select([values]).where(and_(values.c.PATH == path, values.c.LUMISECTION == luminosity, values.c.RUN_NUMBER == run))
            set_properties(stm)
        elif (path and not luminosity and run != None):
            print "QUERY: SELECT * FROM HISTOGRAM_VALUES WHERE RUN_NUMBER =", run, "AND PATH =", path
            stm = select([values]).where(and_(values.c.RUN_NUMBER == run, values.c.PATH == path))
            set_properties(stm)
        elif (path and luminosity and run == None):
            print "QUERY: SELECT * FROM HISTOGRAM_VALUES WHERE LUMISECTION =", luminosity, "AND PATH =", path
            stm = select([values]).where(and_(values.c.PATH == path, values.c.LUMISECTION == luminosity))
            set_properties(stm)
        elif (path and not luminosity and run == None):
            print "QUERY: SELECT * FROM HISTOGRAM_VALUES WHERE PATH =", path
            stm = select([values]).where(values.c.PATH == path)
            set_properties(stm)
        elif (luminosity and run != None):
            print "QUERY: SELECT * FROM HISTOGRAM_VALUES WHERE LUMISECTION =", luminosity, "AND RUN_NUMBER =", run
            stm = select([values]).where(and_(values.c.RUN_NUMBER == run, values.c.LUMISECTION == luminosity))
            set_properties(stm)
        elif (luminosity and run == None):
            print "QUERY: SELECT * FROM HISTOGRAM_VALUES WHERE LUMISECTION =", luminosity
            stm = select([values]).where(values.c.LUMISECTION == luminosity)
            set_properties(stm)
        elif (not luminosity and run != None):
            print "QUERY: SELECT * FROM HISTOGRAM_VALUES WHERE RUN_NUMBER =", run
            stm = select([values]).where(values.c.RUN_NUMBER == run)
            set_properties(stm)

        if (properties[0] == []):
            print "No results!"
            sys.exit(2)
        else:
            print properties

    except e:
        print "ERROR: An error occurred:", e

    if (path):
        print "\nPlots legend:\n ENTRIES\t1\n X_MEAN\t\t2\n X_MEAN_ERROR\t3\n X_RMS\t\t4\n X_RMS_ERROR\t5\n X_UNDERFLOW\t6\n X_OVERFLOW\t7\n Y_MEAN\t\t8\n Y_MEAN_ERROR\t9\n Y_RMS\t\t10\n Y_RMS_ERROR\t11\n Y_UNDERFLOW\t12\n Y_OVERFLOW\t13\n Z_MEAN\t\t14\n Z_MEAN_ERROR\t15\n Z_RMS\t\t16\n Z_RMS_ERROR\t17\n Z_UNDERFLOW\t18\n Z_OVERFLOW\t19\n"

        fig = plt.figure()
        fig.canvas.set_window_title('Histograms\' properties')
        ax = fig.add_subplot(111)
        plt.xticks(lumisections)
        x = lumisections
        y = properties[0]
        plot1, = ax.plot(x, y, 'ro')
        plt.axis([min(x) - 2, max(x) + 2, min(y) * 0.98 - 0.0001,
                  max(y) * 1.02 + 0.0001])  # 0 values generate bottom==top error for axis, thats why +-0.0001
        for xy in zip(x, y):
            ax.annotate(' (%s)' % xy[1], xy=xy, textcoords='data')

        plt.xlabel('Luminosity')
        plt.title(path + '\n' + property_name[4])
        plt.grid()

        ax1 = subplot(111)
        subplots_adjust(bottom=0.25)
        axcolor = 'lightgoldenrodyellow'
        axfreq = axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
        sfreq = Slider(axfreq, 'Property', 1, 18, valinit=1, valfmt='%0.0f')

        annotations = [True, False, False, False, False, False, False, False, False, False, False, False, False, False,
                       False, False, False, False, False]

        def update(val):
            y = properties[int(val) - 1]
            plot1.set_ydata(y)
            ax.set_title(path + '\n' + property_name[int(val) + 3])
            ax.set_ylim([min(y) * 0.98 - 0.0001, max(y) * 1.02 + 0.0001])

            if (not annotations[int(val) - 1]):
                for xy in zip(x, y):  # <--
                    ax.annotate(' (%s)' % xy[1], xy=xy, textcoords='data')
                annotations[int(val) - 1] = True
            draw()

        sfreq.on_changed(update)

        show()


if __name__ == "__main__":
    database = ''
    default_database = 'sqlite:///db1.db'
    isDatabaseSpecified = False
    user = ''
    password = ''

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", help="path to database", type=str)
    parser.add_argument("-u", "--user", help="database username")
    parser.add_argument("-psd", "--password", help="database password")
    parser.add_argument("-r", "--run", help="specify run number for SQL query", type=int)
    parser.add_argument("-l", "--luminosity", help="specify luminosity number for SQL query", type=int)
    parser.add_argument("-p", "--path", help="specify histogram path for SQL query, if you also specify run (but no luminosity), program will display plots of histogram properties vs luminosities")

    args = parser.parse_args()

    if (not args.path and not args.luminosity and args.run == None):
        parser.print_help()
        sys.exit(2)

    if args.database:
        try:
            eng = create_engine(default_database)
            conn = eng.connect()
            print "INFO: Connected to the database"
        except sqlite3.Error as e:
            print "ERROR: An error occurred:", e.args[0]
    else:
        try:
            eng = create_engine(default_database, echo=True)
            conn = eng.connect()
            print "INFO: Connected to the default database"
        except sqlite3.Error as e:
            print "ERROR: An error occurred:", e.args[0]

    meta = MetaData(eng)
    values = Table('histogram_values', meta, autoload=True)

    read_data(conn, values, args.path, args.run, args.luminosity)


