
from datetime import timezone, datetime

print(type(datetime.now(timezone.utc).isoformat()))
