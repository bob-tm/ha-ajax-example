# How to Integrate Ajax security system to Home Assistant

Secure company took the root rights for my hub, so I don't have access to SIA option.

I use Home Assistant Mobile App to forward Ajax notifications from android mobile to HA Server.

I enable Last Notification and Active Notification Count sensors in HA companion app.

On the HA side I use pyscript to parse this data and extract current Ajax status. You can use old android phone (or may be even emulator) just for reporting Ajax status to HA.

I have four zecurity zones that can be armed / disarmed separately. They are: sauna, garage, yard, house

1111 - it's Ajax hub name. Use Search and Replace to put yuor one. 

I upload my pyscript example of parser. You can use this code with small modifications. 

in configuration.yaml  I add custom variable to track ajax status:

<code>
  var:
    ajaxstatus:
      unique_id: "var_ajaxstatus"
      initial_value: "started"
      attributes:
        nightmode: "U"
        sauna    : "U"
        garage   : "U"
        house    : "U"
        yard     : "U"
        alarm    : "U"
        last_notification_time: False
</code>


Change phone sensor name to your one.
<code>
  @state_trigger( "sensor.sm_f916b_last_notification")

  @state_trigger( "sensor.sm_f916b_active_notification_count")
</code>


Left key - zone name in ajax notification
right Value - attribute name in var.ajaxstatus 

<code>
  def parse_ajax_notification(N):	
  	translate_name	= {
  		'дом'   : 'house',
  		'баня'  : 'sauna',
  		'гараж' : 'garage',
  		'двор'  : 'yard',
  		'улица' : 'yard',
  	}
</code>
 
Hope this helps. 
