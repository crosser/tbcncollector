attach :hrldb as hrl;
create table if not exists hrl.data (
	dt int,
	addr text,
	count int,
	batt float,
	mint float,
	temp float,
	maxt float,
	minh float,
	humid float,
	maxh float,
	primary key(dt, addr)
) without rowid;

attach :rawdb as raw;
insert or ignore into hrl.data (dt, addr, count, batt, mint, temp, maxt, minh, humid, maxh)
select strftime("%s", strftime("%Y-%m-%d %H:00:00", dt, "unixepoch")) hour,
       addr,
       count(*) count,
       avg(batt) batt,
       min(temp) mint,
       avg(temp) temp,
       max(temp) maxt,
       min(humid) minh,
       avg(humid) humid,
       max(humid) maxh
from raw.data where dt < strftime("%s", strftime("%Y-%m-%d %H:00:00", unixepoch(), "unixepoch"))
group by strftime("%Y-%m-%d %H", dt, "unixepoch"), addr;

delete from raw.data where dt < strftime("%s", datetime(strftime("%Y-%m-%d %H:00:00"), "-1 hour"));
