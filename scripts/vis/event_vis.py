from scripts.data.models import Event
from matplotlib.widgets import Slider
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import re


def plot_event_map(
    event: Event,
    tight: bool = True,
    save_path: str | None = None,
    padding_deg: float = 1.0,
):
    """
    Plot earthquake event on a Japan map:
      • ▲ triangles for KNET, ■ squares for KIK
      • ★ for epicenter
      • tight zoom around all points if tight=True
      • if save_path is given, saves the figure there

    Parameters:
      event      : Event object
      tight      : whether to zoom to data bounds +/- padding_deg
      save_path  : filepath to save the map (e.g. 'out.png'); if None, no auto-save
      padding_deg: degrees of padding around min/max lat/lon when tight=True
    """
    # 1) Collect all lons/lats (stations + epicenter)
    lons = [event.longitude]
    lats = [event.latitude]
    for st in event.stations.values():
        rd = next(iter(st.readings.values()))
        lons.append(rd.station_long)
        lats.append(rd.station_lat)

    # compute extent
    if tight:
        lon_min, lon_max = min(lons) - padding_deg, max(lons) + padding_deg
        lat_min, lat_max = min(lats) - padding_deg, max(lats) + padding_deg
    else:
        # default Japan box
        lon_min, lon_max = 122, 154
        lat_min, lat_max = 20, 48

    # 2) Set up figure & axes
    fig = plt.figure(figsize=(8, 8 * (lat_max - lat_min) / (lon_max - lon_min)))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

    # 3) Add background
    ax.add_feature(cfeature.LAND.with_scale("50m"))
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"))
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), linestyle=":")

    # 4) Plot stations
    for st in event.stations.values():
        rd = next(iter(st.readings.values()))
        lon, lat = rd.station_long, rd.station_lat

        if st.type().upper() == "KIK":
            marker, label = "s", "KIK"
        else:
            marker, label = "^", "KNET"

        ax.scatter(
            lon,
            lat,
            marker=marker,
            s=60,
            edgecolor="black",
            facecolor="none",
            transform=ccrs.PlateCarree(),
            label=label,
        )

    # 5) Plot epicenter
    ax.scatter(
        event.longitude,
        event.latitude,
        marker="*",
        s=200,
        color="red",
        transform=ccrs.PlateCarree(),
        zorder=5,
        label="Epicenter",
    )

    # 6) Legend & title
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper right")
    ax.set_title(f"Event {event.event_id}  |  Mag {event.magnitude}")

    # 7) Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
        print(f"[+] Map saved to {save_path}")

    plt.show()


def plot_event_vectors(
    event,
    tight: bool = True,
    save_path: str | None = None,
    animate: bool = False,
    padding_deg: float = 1.0,
    cmap="viridis",
    arrow_scale=1e4,
    interval=100,
):
    """
    Vector‐field view of one event:
      • Horizontal arrow = (E–W, N–S) accel at time t
      • Color = U–D accel
      • Two arrows if both surface (…1) and subsurface (…2) exist
      • Slider to scrub time, or animate/export

    Params:
      event      : your Event instance
      tight      : zoom to data ± padding_deg; else full Japan
      save_path  : if provided and animate=False, saves the current frame
      animate    : if True, records an animation to save_path (mp4 or gif)
      padding_deg: degrees padding for tight zoom
      cmap       : matplotlib colormap for vertical accel
      arrow_scale: scaling factor for quiver to look reasonable
      interval   : ms between frames in animation
    """
    # 1) Build station→groups of readings (suffix ""/”1”/”2”)
    stations = {}
    for st in event.stations.values():
        grp = {}
        for rd in st.readings.values():
            m = re.match(r"(.+?)(\d?)$", rd.direction)
            base = m.group(1)
            idx = m.group(2) or "1"  # assume unlabeled is “1”
            grp.setdefault(idx, {})[base] = rd
        stations[st.name] = (st, grp)

    # 2) Determine global time axis (max length & dt)
    max_len = 0
    dt = None
    for st, grp in stations.values():
        for rdict in grp.values():
            for rd in rdict.values():
                L = len(rd)
                if L > max_len:
                    max_len = L
                    if rd.sampling_freq_hz:
                        dt = 1.0 / rd.sampling_freq_hz
    times = np.arange(max_len) * (dt or 1.0)

    # 3) Compute map extent
    lons = [event.longitude]
    lats = [event.latitude]
    for st, grp in stations.values():
        # pick surface group (1) if exists, else any
        base_grp = grp.get("1", next(iter(grp.values())))
        rd0 = next(iter(base_grp.values()))
        lons.append(rd0.station_long)
        lats.append(rd0.station_lat)
    if tight:
        lon0, lon1 = min(lons) - padding_deg, max(lons) + padding_deg
        lat0, lat1 = min(lats) - padding_deg, max(lats) + padding_deg
    else:
        lon0, lon1, lat0, lat1 = 122, 154, 20, 48

    # 4) Create figure, axes, slider
    fig = plt.figure(figsize=(8, 8 * (lat1 - lat0) / (lon1 - lon0)))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([lon0, lon1, lat0, lat1], ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND.with_scale("50m"))
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"))
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), linestyle=":")

    slider_ax = fig.add_axes([0.25, 0.02, 0.5, 0.03])
    slider = Slider(slider_ax, "Time index", 0, max_len - 1, valinit=0, valfmt="%d")

    # 5) Prepare a colormap norm for U–D across all possible values
    all_ud = []
    for st, grp in stations.values():
        for rdict in grp.values():
            if "U-D" in rdict:
                ud = rdict["U-D"]
                # scaled data
                sf = float(ud.scale_factor) if ud.scale_factor else 1.0
                all_ud.append(np.array(ud.data) * sf)
    if all_ud:
        ud_stack = np.concatenate(all_ud)
        vmin, vmax = np.nanpercentile(ud_stack, 1), np.nanpercentile(ud_stack, 99)
    else:
        vmin, vmax = 0, 1

    # 6) The update function: clear & redraw arrows at index i
    def update(i):
        ax.clear()
        ax.set_extent([lon0, lon1, lat0, lat1], ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND.with_scale("50m"))
        ax.add_feature(cfeature.COASTLINE.with_scale("50m"))
        ax.add_feature(cfeature.BORDERS.with_scale("50m"), linestyle=":")

        for st, grp in stations.values():
            # get station coords from surface if possible
            base_grp = grp.get("1", next(iter(grp.values())))
            rd0 = next(iter(base_grp.values()))
            x0, y0 = rd0.station_long, rd0.station_lat

            for idx, axes in grp.items():
                try:
                    # get scaled values at slice i
                    ex = axes["E-W"].to_dataframe(apply_scale=True)["acc"].iloc[i]
                    ey = axes["N-S"].to_dataframe(apply_scale=True)["acc"].iloc[i]
                    ez = axes["U-D"].to_dataframe(apply_scale=True)["acc"].iloc[i]
                except Exception:
                    # fallback: show simple marker
                    m = "s" if st.type().upper() == "KIK" else "^"
                    ax.scatter(
                        x0,
                        y0,
                        marker=m,
                        s=40,
                        transform=ccrs.PlateCarree(),
                        color="gray",
                    )
                    continue

                # color map for ez
                c = plt.cm.get_cmap(cmap)((ez - vmin) / (vmax - vmin))
                # draw arrow
                ax.quiver(
                    x0,
                    y0,
                    ex,
                    ey,
                    transform=ccrs.PlateCarree(),
                    angles="xy",
                    scale_units="xy",
                    scale=arrow_scale,
                    color=c,
                    alpha=0.8,
                    label=f"{st.name} #{idx}",
                )

        # epicenter
        ax.scatter(
            event.longitude,
            event.latitude,
            marker="*",
            s=200,
            color="red",
            transform=ccrs.PlateCarree(),
            zorder=5,
        )

        ax.set_title(f"Event {event.event_id} | slice {i} @ {times[i]:.2f}s")
        return ax

    # initial draw
    update(0)
    slider.on_changed(lambda val: update(int(val)))

    # 7) Animation export if requested
    if animate and save_path:
        anim = animation.FuncAnimation(
            fig, lambda fr: update(fr), frames=max_len, interval=interval, blit=False
        )
        anim.save(save_path)
        print(f"[+] Animation saved to {save_path}")

    # 8) Save single frame if requested
    if (not animate) and save_path:
        plt.savefig(save_path, bbox_inches="tight")
        print(f"[+] Figure saved to {save_path}")

    plt.show()
