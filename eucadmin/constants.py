import os
cfg_dir = os.environ.get('EUCADMIN_CONF_DIR', "/etc/eucadmin")
data_dir = os.environ.get('EUCADMIN_DATA_DIR', "/usr/share/eucadmin")
eucadmin_cfg = os.path.join(cfg_dir, "eucadmin.cfg")
check_path = [ os.path.join(cfg_dir, "check.d"),
               os.path.join(cfg_dir, "mmcheck.d"),
               os.path.join(data_dir, "check.d"),
               os.path.join(data_dir, "mmcheck.d"),
             ]

