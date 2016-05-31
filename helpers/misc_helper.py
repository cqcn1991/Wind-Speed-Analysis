from .shared_imports import *


def generate_Z_from_X_Y(X,Y, Z_func):
    XX, YY=np.meshgrid(X,Y)
    coords=np.array((XX.ravel(), YY.ravel())).T
    Z = Z_func(coords).reshape(XX.shape)
    return Z
