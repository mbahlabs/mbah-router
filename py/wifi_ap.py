import config_file_out
import process
import config
import router_module
import subprocess
import time

config_file_body = """
interface={wifi_ap_if}
logger_syslog=-1
logger_syslog_level=2
logger_stdout=-1
logger_stdout_level=2
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
ssid={wifi_ap_ssid}
hw_mode=g
channel=11
beacon_int=100
dtim_period=2
max_num_sta=255
rts_threshold=2347
fragm_threshold=2346
supported_rates=10 20 55 110 60 90 120 180 240 360 480 540
macaddr_acl=0
ignore_broadcast_ssid=0
wmm_enabled=1
wmm_ac_bk_cwmin=4
wmm_ac_bk_cwmax=10
wmm_ac_bk_aifs=7
wmm_ac_bk_txop_limit=0
wmm_ac_bk_acm=0
wmm_ac_be_aifs=3
wmm_ac_be_cwmin=4
wmm_ac_be_cwmax=10
wmm_ac_be_txop_limit=0
wmm_ac_be_acm=0
wmm_ac_vi_aifs=2
wmm_ac_vi_cwmin=3
wmm_ac_vi_cwmax=4
wmm_ac_vi_txop_limit=94
wmm_ac_vi_acm=0
wmm_ac_vo_aifs=2
wmm_ac_vo_cwmin=2
wmm_ac_vo_cwmax=3
wmm_ac_vo_txop_limit=47
wmm_ac_vo_acm=0
eapol_key_index_workaround=0
eap_server=0
own_ip_addr=127.0.0.1
wpa=2
wpa_passphrase={wifi_ap_passphrase}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
ieee80211n=1
ht_capab=[HT40-][SHORT-GI-40][DSSS_CCK-40]
"""

class WifiAP(router_module.RouterModule):
	def __init__(self, ctx):
		self.config_file = config_file_out.ConfigFileOut(ctx, "hostapd.conf")
		
		conf = config.Config.get_config()

		self.config_file.append(config_file_body.format(**conf))

		router_module.RouterModule.__init__(self, ctx)

	def brutal_stop(self):
		process.shell_command(self.get_context(), "killall hostapd", ignoreResult=True)
		time.sleep(3)

	def start(self):

		conf = config.Config.get_config()
		self.process = process.Process(self.get_context(), "hostapd", "hostapd -B {}".format(self.config_file.get_location()))
		self.process.start()
