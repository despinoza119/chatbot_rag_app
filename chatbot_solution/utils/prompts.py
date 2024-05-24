PROMPT_ABASTORES="""
Genera un query de SQL para la tabla abastores_data, que tiene las siguientes columnas y valores posibles:
1. date: Fecha de la transacción
2. name_product: ['Trigo', 'Cebada', 'Avena', 'Maíz', 'Yeros', 'Centeno', 'Veza', 'Guisantes', 'Pipa', 'Alfalfa', 'Mijo', 'Pipa Girasol', 'Colza']
3. price: Precio del producto
4. source: Fuente del producto
5. province: ['Toledo', 'Sevilla', 'Albacete', 'León', 'Barcelona', 'Palencia', 'Ciudad Real', 'Lleida', 'Zaragoza', 'París', 'Salamanca', 'Segovia', 'Valladolid', 'Cuenca', 'Burgos', 'Córdoba', 'Zamora', 'Estados Unidos']
Usa los valores adecuados para filtrar por producto, fecha, provincia y precio cuando sea relevante. Asegúrate de que la salida sea únicamente el query de SQL, sin texto adicional.
"""