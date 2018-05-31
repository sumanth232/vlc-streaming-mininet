# vlc-streaming-mininet
VLC streaming in Mininet. 2 switches with equal number of hosts connected to each switch

First, place the controllers `2snh_ssim_Controller_congest.py`, `2snh_ssim_Controller_QoS.py` into the right location:
```
$ cp controllers/2snh_ssim_Controller_congest.py ~/pox/pox/misc/
$ cp controllers/2snh_ssim_Controller_QoS.py ~/pox/pox/misc/
```

Decide the number of hosts in the topology - say 4 for example <br>
set the controller file global variable `n = 4` <br>
then, start running the controller `2snh_ssim_Controller_QoS.py`:
```
$ pox/pox.py log.level --DEBUG misc.2snh_ssim_Controller_QoS
```

Run the python script which sets up the topology (with a total of 4 hosts as decided above) and does vlc-streaming:
```
$ sudo ./myvlctest.py 4
```

Please find the attached [Masters Thesis](https://github.com/sumanth232/vlc-streaming-mininet/blob/master/thesis.pdf)

<br>
<br>
Youtube link to stream a video between 2 hosts manually in mininet using VLC media player - https://www.youtube.com/watch?v=dhwXQ5Th58M
