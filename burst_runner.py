import os
import django
import time
import argparse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracking_project.settings")
django.setup()

from core.models import Mapping
from core.services import generate_suffix_burst


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Mapping config_name")
    parser.add_argument("--count", type=int, required=True, help="Number of hits")
    parser.add_argument("--duration", type=int, required=True, help="Total duration in seconds")

    args = parser.parse_args()

    mapping = Mapping.objects.get(config_name=args.config)

    interval = args.duration / args.count

    print(
        f"Running burst for config={args.config} | "
        f"hits={args.count} | duration={args.duration}s | "
        f"interval={interval:.2f}s"
    )

    for i in range(args.count):
        print(f"[{i+1}/{args.count}] Generating suffix")
        generate_suffix_burst(mapping)

        if i < args.count - 1:
            time.sleep(interval)

    print("Burst completed")


if __name__ == "__main__":
    main()
