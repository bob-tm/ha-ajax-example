def copy_all_from_index(A, i):
	result = ''
	while i< len(A):
		#log.info(A[i])
		result = f"{result} {A[i]}"
		i+=1
		
	return result.strip()
	
def parse_ajax_notification(N):
	#log.info(f"Parsing Notification {N}")
	
	# 1111: Гараж armed by Oleksiy Babenko
	# 1111: night mode deactivated by Oleksiy Babenko
	
	A = N.split()
	
	if A[0]!='1111:':
		log.info(f"Ajax skipped {N}")
		return False
		
	group  = False
	armed  = False
	user   = False
	event  = False
	alarm  = False
	text   = False
	
	translate_name	= {
		'дом'   : 'house',
		'баня'  : 'sauna',
		'гараж' : 'garage',
		'двор'  : 'yard',
		'улица' : 'yard',
	}
	
	A12       = f"{A[1]} {A[2]}"
	A12_lower = A12.lower()
	A_last    = A[-1].lower()
	
	# '1111: disarmed by Oleksiy Babenko',
	# '1111: armed by User'
	if (A[1]=='armed') or (A[1]=='disarmed'):
		group = 'all'
		armed = (A[1] == 'armed')
		user  = copy_all_from_index(A, 3)
		
	# '1111: night mode deactivated by Oleksiy Babenko',
	# '1111: night mode activated by Oleksiy Babenko'
	elif (A[1]=='night') and (A[2]=='mode'):
		group = 'nightmode'
		armed = (A[3] == 'activated')
		user  = copy_all_from_index(A, 5)
		
	# '1111: switched on by arming, дом in дом',
	# '1111: switched off by disarming, дом in дом'
	elif (A[1]=='switched'):
		group = translate_name[A[7].lower()]
		armed = (A[2] == 'on')
		user  = False
	# '1111: Двор armed by Oleksiy Babenko',
	# '1111: Баня armed by Oleksiy Babenko',
	# '1111: Гараж disarmed by Oleksiy Babenko'	
	# '1111: дом armed with malfunctions by Oleksiy Babenko'
	# '1111: дом unsuccessful arming attempt by Oleksiy Babenko'
	elif (A[1]=='Дом') or (A[1]=='Баня') or (A[1]=='Гараж') or (A[1]=='Двор'):	
		group = translate_name[A[1].lower()]
		
		# '1111: Двор armed by Oleksiy Babenko',
		if A[2]=='armed' or A[2]=='disarmed':
			armed = (A[2] == 'armed')
			
			# '1111: дом armed with malfunctions by Oleksiy Babenko'
			if A[3]=='with' and A[4]=='malfunctions':
				user  = copy_all_from_index(A, 6)
			else:
				user  = copy_all_from_index(A, 4)
			
		# '1111: дом unsuccessful arming attempt by Oleksiy Babenko'
		elif A[2]=='unsuccessful':
			armed = False
			user  = copy_all_from_index(A, 6)	
			
			
	# '1111: external power failure'
	# '1111: external power restored'
	elif (A[1]=='external') and (A[2]=='power'):	
		#log.info(f"Ajax Power {A[3]}")
		event = True
		text  = copy_all_from_index(A, 1)
		
	# '1111: Hub is online',
	# '1111: Hub is offline. Check the network connection',
	elif (A[1]=='Hub') and (A[2]=='is'):	
		#log.info(f"Ajax Hub is {A[3]}")
		event = True
		text  = copy_all_from_index(A, 1)

	# '1111: Firmware updated',
	# '1111: Updating firmware...',
	elif (A12_lower =='firmware updated') or (A12_lower =='updating firmware...'):	
		#log.info(A12)
		event = True
		text  = copy_all_from_index(A, 1)
		
	# '1111: Motion detected, кухня in дом',
	# '1111: opening detected, sensor in дом',
	# '1111: glass break detected, sensor in дом'	
	elif (A12_lower == 'motion detected,') or (A12_lower == 'opening detected,') or (A12_lower == 'glass break'):	
		#log.info(A12)
		group = translate_name[A_last]
		alarm = True
		text  = copy_all_from_index(A, 1)
	
	# '1111: detector view blocked, check the улица дом in улица
	# '1111: Detector view unblocked, улица дом in улица',
	elif (A12_lower =='detector view'):	
		#log.info(f"Ajax Alarm {N}")
		event = (A[3]=='unblocked,')
		alarm = (A[3]=='blocked,')
		group = translate_name[A_last]
		text  = copy_all_from_index(A, 1)
		
	# '1111: lid is open, комната 1й эт. in дом',
	# '1111: lid is open, зал in дом'
	elif (A12_lower =='lid is') and (A[3]=='open,'):	
		alarm = True
		group = translate_name[A_last]
		text  = copy_all_from_index(A, 1)
		
	# '1111: lid closed, комната 1й эт. in дом',
	elif (A12_lower =='lid closed,'):	
		event = True
		group = translate_name[A_last]
		text  = copy_all_from_index(A, 1)
		
	# '1111: Low battery, сирена баня in баня',
	# '1111: Battery charge is OK, сирена баня іn баня',
	elif (A12_lower == 'low battery,') or (A12_lower == 'battery charge'):
		event = True
		group = translate_name[A_last]
		text  = copy_all_from_index(A, 1)	
		
		
	# '1111: ворота мотор in rapaж is offline. Connection via Jeweller channel lost',
	# '1111: ворота мотор in rapaж is online again. Connection via Jeweller channel restored.',
	# '1111: сирена баня in баня is offline. Connection via Jeweller channel lost.',
	# '1111: сирена баня in баня is online again. Connection via Jeweller channel restored.',
	elif ('Jeweller' in A):
		event = True
		text  = copy_all_from_index(A, 1)		
	else:
		log.info(f"Ajax skipped2 {N}, {A12}")
		return False
		
	return {
		'group': group,
		'armed': armed,
		'user': user,
		'event': event,
		'alarm': alarm,
		'text': text
	}
	

def TimeNow():
	from datetime import datetime as dt
	from datetime import timezone as timezone
	
	return dt.now(tz=timezone.utc)
	
@state_trigger("input_boolean.test")
def Test22():
	AjaxParse ( '1111: Motion detected, кухня in дом' )
	
	return
	AjaxTest = [
				'1111: Гараж armed by Oleksiy Babenko',
				'1111: Двор armed by Oleksiy Babenko',
				'1111: Баня armed by Oleksiy Babenko',
				'1111: дом armed with malfunctions by Oleksiy Babenko',
				'1111: Гараж disarmed by Oleksiy Babenko',
				'1111: night mode deactivated by Oleksiy Babenko',
				'1111: night mode activated by Oleksiy Babenko',
				'1111: Night mode activated with malfunctions by Oleksiy Babenko',
				'1111: Unsuccessful Night mode activation attempt by Oleksiy Babenko',
				'1111: дом unsuccessful arming attempt by Oleksiy Babenko',
				'1111: armed by User',
				'1111: disarmed by Oleksiy Babenko',
				'1111: switched on by disarming, дом in дом',
				'1111: switched off by disarming, дом in дом',
				'1111: external power failure',
				'1111: external power restored',
				'1111: Temporarily deactivated, ворота мотор in гараж.',
				'1111: Hub is online',
				'1111: Hub is offline. Check the network connection',
				'1111: Low battery, сирена баня in баня',
				'1111: Battery charge is OK, сирена баня іn баня',
				'1111: ворота мотор in rapaж is offline. Connection via Jeweller channel lost',
				'1111: ворота мотор in rapaж is online again. Connection via Jeweller channel restored.',
				'1111: сирена баня in баня is offline. Connection via Jeweller channel lost.',
				'1111: сирена баня in баня is online again. Connection via Jeweller channel restored.',
				'1111: Firmware updated',
				'1111: Updating firmware...',
				'1111: lid is open, комната 1й эт. in дом',
				'1111: lid closed, комната 1й эт. in дом',
				'1111: lid is open, зал in дом',
				'1111: Motion detected, кухня in дом',
				'1111: opening detected, sensor in дом',
				'1111: glass break detected, sensor in дом',
				'1111: Detector view blocked, check the улица дом in улица',
				'1111: Detector view unblocked, улица дом in улица'
		]
		
	
	AjaxAlarm = [
				'1111: Motion detected, кухня in дом',
				'1111: opening detected, sensor in дом',
				'1111: glass break detected, sensor in дом',
				'1111: Detector view blocked, check the улица дом in улица',
				'1111: lid is open, комната 1й эт. in дом',
				'1111: lid is open, зал in дом'
		]
	
	
	log.info("\n\nTest")
	for N in AjaxTest: 
		R = parse_ajax_notification(N)
		if R:
			#if R['event']:
			#	log.info(f"{R['text']} - {R['group']}")
			
			#if R['alarm']:
			#	log.info(f"{R['text']} - {R['group']}")
			
			if (R['event'] == False) and (R['alarm'] == False):
				log.info(f"{R['armed']} - {R['text']} - {R['group']}")

'''	
@state_trigger("input_boolean.test")
def Test():
	#N = '1111: Двор armed by Oleksiy Babenko'
	#AjaxParse(N)
	log.info("test")
	ParseActiveNotificationCount('sensor.sm_f916b_active_notification_count')
'''
		
def ParseActiveNotificationCount(e): 
	R = ParseActiveNotificationCountAttr(e)
	#log.info(R)

	for time,text in R.items():
		log.info(f"New Attr Ajax Notification: {text}, {TimeToHuman(time)}, Time {time}")
		AjaxParse(text)
		var.ajaxstatus.last_notification_time = time
	
def TimeToHuman(time):
	from datetime import datetime
	return datetime.fromtimestamp(time / 1000)
	
def ParseActiveNotificationCountAttr(e):
	A = state.getattr(e)
	
	L = {}
	for k,v in A.items():
		# android.bigText_com.ajaxsystems_1026061
		# android.text_com.ajaxsystems_1026061
		# com.ajaxsystems_1026061_post_time
		if k.startswith('android.text_com.ajaxsystems'):
			s = k.rsplit("_", 1)
			pt = f"com.ajaxsystems_{s[1]}_post_time"
			#log.info(f"{A[pt]} : {v}")
			L[int(A[pt])]= v
			
	SortedL = sorted(L.items())
	Result = {}
	
	try:
		last_notification_time = int(var.ajaxstatus.last_notification_time)
	except (TypeError, ValueError):
		last_notification_time = 0
	
	for time, text in SortedL:
		if time > last_notification_time:
			#log.info(f"New {time}:{text}")
			Result[time]=text
		else:
			#log.info(f"Skip {TimeToHuman(time)}, {time} :{text}")
			pass
			
	return Result	
		
def VarAjaxSetAll(armed):
	log.info(f"Set all to {armed}")
	var.ajaxstatus.house  = armed
	var.ajaxstatus.sauna  = armed
	var.ajaxstatus.garage = armed
	var.ajaxstatus.yard   = armed
	
	if not armed:
		var.ajaxstatus.nightmode   = armed

def b2c(x,c):
	if x:
		return c
	else:
		return '_'
		
def AjaxParse(N):
	R = parse_ajax_notification(N)
	'''
	nightmode: null
	sauna: null
	garage: null
	house: null
	yard: null
	alarm: null
	'''
	if R:
		ajax_prev = var.ajaxstatus
		
		if R['alarm']:
			var.ajaxstatus.alarm      = True
			var.ajaxstatus.alarm_time = TimeNow()
			on_ajax_alarm(R)
				
		if R['event']:
			log.info(f"Ajax Event: {R['text']}")
			
			
		elif R['group']=='all':
			VarAjaxSetAll(R['armed'])
		else:
			attr = f"var.ajaxstatus.{R['group']}"
			log.info(f"Set {attr} to {R['armed']}")
			state.setattr(attr, R['armed'])

		var.ajaxstatus = f"{b2c(var.ajaxstatus.yard, 'y')}{b2c(var.ajaxstatus.garage, 'g')}{b2c(var.ajaxstatus.sauna, 's')}{b2c(var.ajaxstatus.house, 'h')}{b2c(var.ajaxstatus.nightmode, 'n')}"
		on_ajax_changed(ajax_prev, R)
	
def on_ajax_alarm(R):
	log.info(f"Ajax Alarm: {R['text']}")
			
	params = {'text': R['text'], 'group': R['group']}
	event.fire('on_ajax_alarm', **params)
	
	#notify.telegram_call(message=R['text'], blocking=True)
			
def on_ajax_changed(old_ajaxstatus, R):
	
	if old_ajaxstatus.garage != var.ajaxstatus.garage:
		log.info(f"|- Ajax Garage Changed from {old_ajaxstatus.garage} to {var.ajaxstatus.garage}")
		MQTT.Publish(topic="cmnd/garage/armed", payload=f"{var.ajaxstatus.garage}", retain=True)
		
		if var.ajaxstatus.garage:
			state.set('input_boolean.garage_gate', 'armed')
			switch.turn_off(entity_id='switch.gate_garage')
			switch.turn_off(entity_id='switch.gate_yard')
		
			light.turn_off(entity_id='light.garage_inside')
			light.turn_off(entity_id='light.garage_inside_12v')
		else:
			state.set('input_boolean.garage_gate', 'off')
			
			import func
			x = func.ValueSecondsAgo('var.ajaxstatus', 30)['s']
			
			# x = 'ygsh_'
			# if house was armed 30 seconds ago and garage is disarmed -> we get back to home
			if (x[3]=='h'):
				log.info("Garage disarmed: Enabling Gates Power")
				# таймер автоотключения
				mqtt.publish(topic="cmnd/tasmota_9AF03C/Backlog", payload=f"TurnOnInvertorByRF reset_off_timers,0")
				switch.turn_on(entity_id='switch.gate_garage')
				switch.turn_on(entity_id='switch.gate_yard')	
	
	#if (R['group']=='all') or (R['group']=='garage'):
	#	log.info(f"|- Ajax Garage Changed to {var.ajaxstatus.garage}")
	#	MQTT.Publish(topic="cmnd/garage/armed", payload=f"{var.ajaxstatus.garage}", retain=True)
		
	if var.ajaxstatus.house or var.ajaxstatus.nightmode:
		switch.turn_on(entity_id='switch.house_enterance_led_in_button')
	else:
		switch.turn_off(entity_id='switch.house_enterance_led_in_button')
		var.ajaxstatus.alarm = False
	
@state_trigger( "sensor.sm_f916b_last_notification")
@state_trigger( "sensor.sm_f946b_last_notification")
def on_ajax_notification(**kwargs):
	N = state.get(kwargs['var_name'])
	log.info(f"Last Ajax Notification {N}")
	AjaxParse(N)
	
@state_trigger( "sensor.sm_f916b_active_notification_count")
@state_trigger( "sensor.sm_f946b_active_notification_count")
def on_ajax_notification2(**kwargs):
	ParseActiveNotificationCount(kwargs['var_name'])				
			
@state_trigger( "binary_sensor.line_power != 'unavailable' and binary_sensor.line_power.old == 'unavailable'")
def on_garage_back_online():
	log.info("Update Garage Arm Status") 
	MQTT.Publish(topic="cmnd/garage/armed", payload=f"{var.ajaxstatus.garage}", retain=True)