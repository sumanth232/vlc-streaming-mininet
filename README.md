# vlc-streaming-mininet
VLC streaming in Mininet. 2 switches with equal number of hosts connected to each switch

First, place the controllers `2snh_ssim_Controller_congest.py`, `2snh_ssim_Controller_QoS.py` into the right location:
```
cp controllers/2snh_ssim_Controller_congest.py ~/pox/pox/misc/
cp controllers/2snh_ssim_Controller_QoS.py ~/pox/pox/misc/
```

Decide the number of hosts in the topology - say 4 for example
set the controller file global variable `n = 4`
then, start running the controller `2snh_ssim_Controller_QoS.py`:
```
pox/pox.py log.level --DEBUG misc.2snh_ssim_Controller_QoS
```

Run the python script which sets up the topology (with a total of 4 hosts as decided above) and does vlc-streaming:
```
sudo ./n_myvlctest.py 4
```