import osmnx as ox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import pydeck as pdk

# Ввод координат точки города от пользователя
x0 = float(input("Введите широту точки: "))
y0 = float(input("Введите долготу точки: "))

# Загрузка данных из CSV файла
data = pd.read_csv('measurements.csv', delimiter=';')

# Пользователь выбирает загрязнение
pollution_type = input("Выберите тип загрязнения (nh3, co, no2, dust): ")
mean_pollution = data[pollution_type].mean()

# Интерполяционные параметры
k = 1.86  # коэффициент диффузии
mean_wind_speed = data['wind_speed'].mean()
#x0, y0 = ox.utils.unproject_point((latitude, longitude))
x1 = x0 + 0.001213
y1 = y0 + 0.000918

# Создание сетки координат
x = np.linspace(x0 - 0.01, x0 + 0.01, 100)
y = np.linspace(y0 - 0.01, y0 + 0.01, 100)
X, Y = np.meshgrid(x, y)

# Интерполяция для определения распространения загрязнения
pollution_values = (mean_pollution / (2 * 3.14 * k**2 * mean_wind_speed)) * np.exp(-(((X - x1)**2 + (Y - y1)**2) / (2 * k**2)))

# Создание трехмерной модели и визуализация
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, pollution_values, cmap='viridis')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Pollution Level')
plt.title(f'{pollution_type.capitalize()} Distribution')

plt.show()
