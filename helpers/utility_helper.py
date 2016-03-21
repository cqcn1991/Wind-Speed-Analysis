from .shared_imports import *

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def plot_3d_prob_density(X,Y,Z, ax = None):
    if ax is None:
        fig = plt.figure()
        fig.set_size_inches(14, 8)
        ax = fig.gca(projection='3d')
    ax.set_aspect('equal')
    X, Y = np.meshgrid(X, Y)
    surf = ax.plot_surface(
        X, Y, Z,rstride=1, cstride=1, cmap='jet',
        linewidth=0, antialiased=False)

def plot_2d_prob_density(X,Y,Z,ax = None):
#   For docs, see `help(plt.contour)`
    if ax is None:
        fig, ax = plt.subplots()
        fig.set_size_inches(14, 8)
    ax.set_aspect('equal')
    CS = plt.contourf(X, Y, Z, 10, alpha=.75, cmap='jet')
    plt.colorbar(CS)

def generate_Z_from_X_Y(X,Y, Z_func):
    XX,YY=np.meshgrid(X,Y)
    coords=np.array((XX.ravel(), YY.ravel())).T
    Z = Z_func(coords).reshape(XX.shape)
    return Z