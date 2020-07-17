import ipyvuetify as v
from datetime import datetime

def displayIO(widget_alert, alert_type, message):
    """ Display the message in a vuetify alert DOM object with specific coloring
    Args: 
        widget_alert (v.Alert) : the vuetify alert to modify
        alert_type (str) : the change the alert color
        message (v.Children) : a DOM element or a string to fill the message 
    """
    
    list_color = ['info', 'success', 'warning', 'error']
    if not alert_type in list_color:
        alert_type = 'info'
        
    widget_alert.type = alert_type
     
    current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
    widget_alert.children = [
        v.Html(tag='p', children=['[{0}]'.format(current_time)]),
        v.Html(tag='p', children=[message])
   ]

def toggleLoading(btn):
    """Toggle the loading state for a given btn in the ipyvutify lib
    
    Args:
        btn (v.Btn) : the btn to toggle
    """
    
    btn.loading = not btn.loading
    btn.disabled = btn.loading