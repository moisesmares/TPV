from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup

inventario = [
{'codigo': '001', 'nombre': 'Taco de suadero', 'precio': 25.0, 'cantidad': 30},
{'codigo': '002', 'nombre': 'Taco al pastor', 'precio': 25.0, 'cantidad': 30},
{'codigo': '003', 'nombre': 'Taco de arrachera', 'precio': 30.0, 'cantidad': 30}
]

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behavior to the view. '''
    touch_deselect_last = BooleanProperty(True)

class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad_carrito'])
        self.ids['_precio_unitario'].text = str("{:.2f}".format(data['precio']))
        self.ids['_precio_total'].text = str("{:.2f}".format(data['precio_total']))
        return super(SelectableBoxLayout, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayout, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
        	return self.parent.select_with_touch(self.index, touch)
        	print(f"Item at index {self.index} touched")

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        print(f"Item at index {index} selected. {is_selected}")
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False

class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_codigo'].text = data['codigo']
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio'].text = str("{:.2f}".format(data['precio']))
        return super(SelectableBoxLayoutPopup, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayoutPopup, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
            print(f"Popup item at index {self.index} touched")

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        print(f"Popup item at index {index} selected: {is_selected}")
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False


class RV(RecycleView):

    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []
        self.modificar_producto = None

    def agregar_articulo(self, articulo):
    	articulo['seleccionado'] = False
    	indice = -1
    	if self.data:
    		for i in range(len(self.data)):
    			if articulo['codigo'] == self.data[i]['codigo']:
    				indice = i

    		if indice >=0:
    			self.data[indice]['cantidad_carrito'] += 1
    			self.data[indice]['precio_total'] = self.data[indice]['precio']*self.data[indice]['cantidad_carrito']
    			self.refresh_from_data()
    		else:
    			self.data.append(articulo)
    	else:
    		self.data.append(articulo)

    def eliminar_articulo(self):
    	print("Llamó a rv.eliminar_articulo")
    	indice = self.articulo_seleccionado()
    	precio = 0
    	print(f"Selected index: {indice}")
    	if indice >= 0:
    		self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
    		precio = self.data[indice]['precio_total']
    		self.data.pop(indice)
    		self.refresh_from_data()
    	return precio

    def articulo_seleccionado(self):
    	print("Llamó a articulo_seleccionado")
    	indice = -1
    	for i in range(len(self.data)):
    		if self.data[i]['seleccionado']:
    			indice = i
    			break
    	print(f"Selected article index: {indice}")
    	return indice

    def modificar_articulo(self):
    	indice = self.articulo_seleccionado()
    	if indice >=0:
    		popup = CambiarCantidadPopup(self.data[indice], self.actualizar_articulo)
    		popup.open()

    def actualizar_articulo(self, valor):
    	indice = self.articulo_seleccionado()
    	if indice >= 0:
    		if valor == 0:
    			self.data.pop(indice)
    			self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
    		else:
    			self.data[indice]['cantidad_carrito'] = valor
    			self.data[indice]['precio_total'] = self.data[indice]['precio']*valor
    		self.refresh_from_data()
    		nuevo_total = 0
    		for data in self.data:
    			nuevo_total+= data['precio_total']
    		self.modificar_producto(False, nuevo_total)

class CambiarCantidadPopup(Popup):

	def __init__(self, data, actualizar_articulo_callback, **kwargs):
		super(CambiarCantidadPopup, self).__init__(**kwargs)
		self.data = data
		self.actualizar_articulo = actualizar_articulo_callback
		self.ids.info_nueva_cantidad_1.text = "Producto: " + self.data['nombre'].capitalize()
		self.ids.info_nueva_cantidad_2.text = "Cantidad: " + str(self.data['cantidad_carrito'])

	def validar_input(self, texto_input):
		if texto_input.isdigit():
			nueva_cantidad = int (texto_input)
			self.ids.notificacion_no_valido.text = ''
			self.actualizar_articulo(nueva_cantidad)
			self.dismiss()
		else:
			self.ids.notificacion_no_valido.text = 'Cantidad no valida'

class ProductoPorNombrePopup(Popup):
	def __init__(self, input_nombre, agregar_producto_callback, **kwargs):
		super(ProductoPorNombrePopup, self).__init__(**kwargs)
		self.input_nombre = input_nombre
		self.agregar_producto = agregar_producto_callback


	def mostrar_articulos(self):
		self.open()
		for nombre in inventario:
			if nombre['nombre'].lower().find(self.input_nombre)>=0:
				producto={'codigo': nombre['codigo'], 'nombre': nombre['nombre'],
				'precio': nombre['precio'], 'cantidad': nombre['cantidad']}
				self.ids.rvs.agregar_articulo(producto)

	def seleccionar_articulo(self):
		indice = self.ids.rvs.articulo_seleccionado()
		if indice >=0:
			_articulo = self.ids.rvs.data[indice]
			articulo ={}
			articulo['codigo'] = _articulo['codigo']
			articulo['nombre'] = _articulo['nombre']
			articulo['precio'] = _articulo['precio']
			articulo['cantidad_carrito'] = 1
			articulo['cantidad_inventario'] = _articulo['cantidad']
			articulo['precio_total'] = _articulo['precio']
			if callable(self.agregar_producto):
				self.agregar_producto(articulo)
			self.dismiss()

class VentasWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total = 0.0
        self.ids.modificar_producto = self.modificar_producto

    def agregar_producto_codigo(self, codigo):
    	for producto in inventario:
    		if codigo == producto['codigo']:
    			articulo={}
    			articulo['codigo']=producto['codigo']
    			articulo['nombre']=producto['nombre']
    			articulo['precio']=producto['precio']
    			articulo['cantidad_carrito']=1
    			articulo['cantidad_inventario']=producto['cantidad']
    			articulo['precio_total']=producto['precio']
    			self.agregar_producto(articulo)
    			self.ids.buscar_codigo.text = ''
    			break

    def agregar_producto_nombre(self, nombre):
    	self.ids.buscar_nombre.text = ''
    	popup= ProductoPorNombrePopup(nombre, self.agregar_producto)
    	popup.mostrar_articulos()

    def agregar_producto(self, articulo):
    	self.total+=articulo['precio']
    	self.ids.subtotal.text = '$ '+ "{:.2f}".format(self.total)
    	self.ids.rvs.agregar_articulo(articulo)

    def eliminar_articulo(self):
    	print("eliminar_articulo called")
    	menos_precio = self.ids.rvs.eliminar_articulo()
    	print(f"menos_precio: {menos_precio}")
    	self.total -= menos_precio
    	self.ids.subtotal.text = '$ '+"{:.2f}".format(self.total)

    def modificar_producto(self, cambio=True, nuevo_total = None):
    	if cambio:
    		self.ids.rvs.modificar_producto()
    	else:
    		self.total = nuevo_total
    		self.ids.subtotal.text = '$ '+"{:.2f}".format(self.total)

    def pagar(self):
   		print("pagar")

    def nueva_compra(self):
   		print("nueva_compra")

    def admin(self):
    	print("Admin presionado")

    def salir(self):
    	print("Salir presionado")


class VentasApp(App):
    def build(self):
        return VentasWindow()

if __name__ == '__main__':
    VentasApp().run()