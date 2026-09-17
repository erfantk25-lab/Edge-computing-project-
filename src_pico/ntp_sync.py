import ntptime
from time import sleep, time

NTP_EPOCH_OFFSET = 946684800  # seconds between 1970-01-01 and 2000-01-01

def sync_time(retries=3):
    """Sync the Pico's clock to a NTP-server (UTC).
    
    Requires wifi-connection. 

    Args:
        retries: Number of sync attempts. 

    Returns:
        True if the sync succeeded, False if all attemps failed. 
    """
    for attempt in range(retries):
        try:
            ntptime.settime()   # ntptime is an built-in clock function
            print("Time synced:", time())
            return True
        except OSError as e:
            print(f"NTP sync failed (attempt {attempt + 1}/{retries})", e)
            sleep(2)
    print("Could nor sync time after", retries, "attemps")
    return False

def unix_time():
    """Return current time as Unix seconds.

    MicroPython on the Pico counts seconds from 2000-01-01,
    not the standard Unix epoch (1970-01-01), so NTP_EPOCH_OFFSET
    converts to a value compatible with e.g. Postgres to_timestamp().
    """
    return time() + NTP_EPOCH_OFFSET