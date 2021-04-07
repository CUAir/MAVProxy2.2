import matplotlib.pyplot as plt
import shapely.geometry as sg
import numpy as np
# class to manage waypoints and obstacles to plot
class Plot(object):
    def __init__(self,geofence,splines=None,obstacles=None,function=None):
        fig,ax=plt.subplots()
        # set bounds of the graph based on the bounding box of the geofence
        minx, miny, maxx, maxy = geofence.bounds
        plt.xlim(minx,maxx)
        plt.ylim(miny,maxy)
        # plot the outline of the geofence
        x,y = geofence.exterior.xy
        ax.plot(x,y,color='r',linewidth=3)
        if splines:
            waypoints = splines.get_waypoints()
            ax.plot(waypoints[0],waypoints[1],'bo')
            xs,ys = splines.get_graphable()
            ax.plot(xs,ys,'r')
        if obstacles:
            #plt.Circle((obstacles[0][0], obstacles[0][1]), obstacles[1], color='g')
            for i in range(len(obstacles[0][0])):
                circle = plt.Circle((obstacles[0][0][i], obstacles[0][1][i]), obstacles[1][i],facecolor='none',edgecolor='g')
                #circle = plt.Circle((30,30),10)
                ax.add_patch(circle)
                #plt.plot(obstacles[0][0][i],obstacles[0][1][i],'go',markersize=obstacles[1][i])
        if function:
            x,y = np.meshgrid(np.linspace(minx, maxx, 200), np.linspace(miny, maxy, 100))
            z = function(x,y)
            z_min, z_max = -np.abs(z).max(), np.abs(z).max()
            #print(z_min)
            #print(z_max)
            z_min = -100
            z_max = 100
            #print(z.shape)
            #print(z)
            #print(x.shape)
            c = ax.pcolormesh(x, y, z, cmap='RdBu', vmin=z_min, vmax=z_max)
            fig.colorbar(c, ax=ax)
    # show the plot
    def show(self):
        #plt.xlim(-100, 100)
        #plt.ylim(-100, 100)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()





        
