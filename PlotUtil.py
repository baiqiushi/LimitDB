import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
from itertools import cycle


lines = ["-", "--", "-.", ":"]
markers = ['o', '^', '*', '+', 'x', 'd', 's', 'p']
lineCycler = cycle(lines)
makerCycler = cycle(markers)


# plot given p_curves into one image
# p_labels: a list of labels with same order of list of curves in p_curves, format ['label0', 'label1', ..., 'labelN']
# p_x: a list of x axis values with same order of list of curves in p_curves, format [x0, x1, x2, ..., xM]
# p_curves: in the format as [[y0, y1, y2, ..., yM](curve0), [y0, y1, y2, ..., yM](curve1), ..., (curveN)]
#           a list of list, totally N curves, for each curve there're M values
# p_x_label: label for x axis
# p_y_label: label for y axis
def plotCurves(p_fileName, p_labels, p_x, p_curves, p_x_label, p_y_label, p_title, p_showLegend=True):
    pp = PdfPages(p_fileName + '.pdf')
    plt.figure()
    n = 0
    for i_label in p_labels:
        plt.plot(p_x, p_curves[n], label=i_label, marker=next(makerCycler))
        n += 1
    plt.xlabel(p_x_label)
    plt.ylabel(p_y_label)
    plt.title(p_title)
    plt.grid(True)
    if p_showLegend:
        plt.legend()
    plt.savefig(pp, format='pdf')
    pp.close()


# def plotSurface(p_fileName, p_x, p_y, p_z, p_x_label, p_y_label, p_z_label, p_title, p_angle):
#     pp = PdfPages(p_fileName + '.pdf')
#     fig = plt.figure()
#     ax = fig.gca(projection='3d')
#     ax.plot_surface(p_x, p_y, p_z, rstride=8, cstride=8, alpha=0.3)
#     cset = ax.contour(p_x, p_y, p_z, zdir='z', cmap=cm.coolwarm)
#     cset = ax.contour(p_x, p_y, p_z, zdir='x', cmap=cm.coolwarm)
#     cset = ax.contour(p_x, p_y, p_z, zdir='y', cmap=cm.coolwarm)
#     ax.set_xlabel(p_x_label)
#     ax.set_ylabel(p_y_label)
#     ax.set_zlabel(p_z_label)
#     ax.view_init(30, p_angle)
#     plt.title(p_title)
#     plt.savefig(pp, format='pdf')
#     pp.close()
