import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { doctorsApi } from "@/api/doctors";
import { routesApi } from "@/api/operations";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  EmptyState,
  ErrorState,
  LoadingSkeleton,
} from "@/components/feedback/States";
import { GOOGLE_MAPS_API_KEY } from "@/constants/env";

type MapStop = {
  hcp_id: string;
  sequence: number;
  latitude: number | null;
  longitude: number | null;
};
type PlanStop = MapStop & {
  name: string;
  priority_score: number;
  travel_minutes: number;
  planned_arrival_at: string;
};

function RouteMap({ stops }: { stops: MapStop[] }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [mapReady, setMapReady] = useState(false);
  const [mapError, setMapError] = useState("");

  const points = useMemo(
    () => stops.filter((stop) => stop.latitude !== null && stop.longitude !== null),
    [stops],
  );

  useEffect(() => {
    if (!GOOGLE_MAPS_API_KEY) {
      setMapError("Add VITE_GOOGLE_MAPS_API_KEY to enable the Google Maps view.");
      setMapReady(false);
      return;
    }

    const googleMaps = (window as Window & { google?: { maps: any } }).google?.maps;
    if (googleMaps) {
      setMapReady(true);
      setMapError("");
      return;
    }

    const existingScript = document.querySelector<HTMLScriptElement>(
      'script[src*="maps.googleapis.com/maps/api"]',
    );

    const handleLoad = () => {
      setMapReady(true);
      setMapError("");
    };

    const handleError = () => {
      setMapError("Google Maps failed to load. Check the API key and enabled APIs.");
      setMapReady(false);
    };

    if (existingScript) {
      if (existingScript.dataset.loaded === "true") {
        handleLoad();
      } else {
        existingScript.addEventListener("load", handleLoad);
        existingScript.addEventListener("error", handleError);
      }
      return () => {
        existingScript.removeEventListener("load", handleLoad);
        existingScript.removeEventListener("error", handleError);
      };
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=maps`;
    script.async = true;
    script.defer = true;
    script.addEventListener("load", handleLoad);
    script.addEventListener("error", handleError);
    document.head.appendChild(script);

    return () => {
      script.removeEventListener("load", handleLoad);
      script.removeEventListener("error", handleError);
    };
  }, []);

  useEffect(() => {
    if (!mapReady || !mapRef.current || !points.length) return;

    const googleMaps = (window as Window & { google?: { maps: any } }).google?.maps;
    if (!googleMaps) return;

    const center = {
      lat: points.reduce((sum, point) => sum + (point.latitude as number), 0) / points.length,
      lng: points.reduce((sum, point) => sum + (point.longitude as number), 0) / points.length,
    };

    const map = new googleMaps.Map(mapRef.current, {
      center,
      zoom: 10,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });

    const bounds = new googleMaps.LatLngBounds();
    const routePath = points.map((point) => ({
      lat: point.latitude as number,
      lng: point.longitude as number,
    }));

    routePath.forEach((position, index) => {
      bounds.extend(position);
      new googleMaps.Marker({
        position,
        map,
        label: String(points[index].sequence),
      });
    });

    if (routePath.length > 1) {
      map.fitBounds(bounds);
    } else {
      map.setCenter(center);
      map.setZoom(12);
    }

    new googleMaps.Polyline({
      path: routePath,
      geodesic: true,
      strokeColor: "#2563eb",
      strokeOpacity: 0.9,
      strokeWeight: 3,
      map,
    });
  }, [mapReady, points]);

  if (!points.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-xl border bg-muted text-sm text-muted-foreground">
        No coordinates available for the selected HCPs.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {mapError ? (
        <div className="flex h-72 items-center justify-center rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
          {mapError}
        </div>
      ) : (
        <div ref={mapRef} className="h-72 w-full rounded-xl border" />
      )}
      <p className="text-xs text-muted-foreground">
        Google Maps view with route markers and a travel path.
      </p>
    </div>
  );
}

export function RoutesPage() {
  const qc = useQueryClient();
  const itineraryRef = useRef<HTMLDivElement>(null);
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [selected, setSelected] = useState<string[]>([]);
  const [location, setLocation] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);
  const [locationError, setLocationError] = useState("");
  const doctors = useQuery({
    queryKey: ["route-doctors"],
    queryFn: () =>
      doctorsApi.list({ limit: 100, sort: "last_name", status: "active" }),
  });
  const routes = useQuery({ queryKey: ["routes"], queryFn: routesApi.list });
  const plan = useMutation({
    mutationFn: () =>
      routesApi.plan({
        route_date: date,
        hcp_ids: selected,
        workday_start: `${date}T08:00:00Z`,
        workday_end: `${date}T18:00:00Z`,
        origin_latitude: location?.latitude,
        origin_longitude: location?.longitude,
      }),
       onSuccess: () => {
    setTimeout(() => {
      itineraryRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 100);
  },
  });
  


  const create = useMutation({
    mutationFn: () =>
      routesApi.create({
        name: `HCP plan — ${date}`,
        route_date: date,
        stops: selected.map((hcp_id) => ({ hcp_id })),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["routes"] });
      setSelected([]);
    },
  });
  const suggested = useMemo(
    () =>
      [...(doctors.data ?? [])].sort(
        (a, b) =>
          b.engagement_score +
          b.prescription_trend -
          (a.engagement_score + a.prescription_trend),
      ),
    [doctors.data],
  );
  if (doctors.isLoading || routes.isLoading) return <LoadingSkeleton />;
  if (doctors.error || routes.error)
    return (
      <ErrorState
        message={((doctors.error || routes.error) as Error).message}
      />
    );
  const plannedStops = (plan.data?.stops ?? []) as PlanStop[];
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-bold">HCP route planner</h1>
        <p className="text-muted-foreground">
          Select accounts and calculate a weighted itinerary using priority,
          urgency, distance, travel time, and working hours.
        </p>
      </div>
      <Card>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <label className="text-sm font-medium">
            Visit date{" "}
            <input
              className="ml-2 rounded border p-2"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </label>
          <div className="flex flex-wrap gap-2">
            <Button
              className="bg-muted text-foreground"
              onClick={() =>
                navigator.geolocation.getCurrentPosition(
                  (position) => {
                    setLocation({
                      latitude: position.coords.latitude,
                      longitude: position.coords.longitude,
                    });
                    setLocationError("");
                  },
                  () =>
                    setLocationError(
                      "Location permission was unavailable. The planner will use the first HCP as its starting point.",
                    ),
                )
              }
            >
              {location ? "Location captured" : "Use current location"}
            </Button>
            <Button
              disabled={!selected.length || plan.isPending}
              onClick={() => plan.mutate()}
            >
              Calculate itinerary
            </Button>
            <Button
              disabled={!selected.length || create.isPending}
              onClick={() => create.mutate()}
            >
              Save route
            </Button>
          </div>
        </div>
        {location && (
          <p className="mb-2 text-xs text-emerald-700">
            Starting point: {location.latitude.toFixed(5)},{" "}
            {location.longitude.toFixed(5)}
          </p>
        )}
        {locationError && (
          <p className="mb-2 text-xs text-amber-700">{locationError}</p>
        )}
        {suggested.length ? (
          suggested.map((doctor) => (
            <label
              className="flex cursor-pointer items-center justify-between border-b py-3"
              key={doctor.id}
            >
              <span>
                <input
                  className="mr-3"
                  type="checkbox"
                  checked={selected.includes(doctor.id)}
                  onChange={(e) =>
                    setSelected((ids) =>
                      e.target.checked
                        ? [...ids, doctor.id]
                        : ids.filter((id) => id !== doctor.id),
                    )
                  }
                />
                <b>
                  {doctor.first_name} {doctor.last_name}
                </b>
                <span className="ml-3 text-sm text-muted-foreground">
                  Priority signal{" "}
                  {Math.round(
                    doctor.engagement_score + doctor.prescription_trend,
                  )}
                </span>
              </span>
              <span className="text-sm text-muted-foreground">
                {doctor.status}
              </span>
            </label>
          ))
        ) : (
          <EmptyState
            title="No active HCPs"
            description="Add accounts before planning a route."
          />
        )}
      </Card>
      {plan.data && (
        <div ref={itineraryRef}>
        <Card>
          <div className="mb-3 flex flex-wrap items-center justify-between">
            <h2 className="font-semibold">Optimized itinerary</h2>
            <span className="text-sm text-muted-foreground">
              {plan.data.distance_km} km · {plan.data.total_minutes} minutes
            </span>
          </div>
          <RouteMap stops={plan.data.map_stops as MapStop[]} />
          <div className="mt-4 grid gap-2">
            {plannedStops.map((stop) => (
              <div className="rounded-lg border p-3" key={stop.hcp_id}>
                <b>
                  {stop.sequence}. {stop.name}
                </b>
                <span className="ml-3 text-sm">
                  Priority {stop.priority_score}
                </span>
                <span className="ml-3 text-sm text-muted-foreground">
                  {new Date(stop.planned_arrival_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}{" "}
                  · {stop.travel_minutes} min travel
                </span>
              </div>
            ))}
          </div>
          
        </Card></div>
      )}
      <Card>
        <h2 className="mb-3 font-semibold">Saved plans</h2>
        {routes.data?.length ? (
          routes.data.map((route) => (
            <div
              className="flex items-center justify-between border-b py-3"
              key={route.id}
            >
              <span>
                <b>{route.name}</b> — {route.route_date} ({route.status})
              </span>
              <Button
                onClick={() =>
                  routesApi
                    .optimize(route.id)
                    .then(() => qc.invalidateQueries({ queryKey: ["routes"] }))
                }
              >
                Re-optimize
              </Button>
            </div>
          ))
        ) : (
          <EmptyState
            title="No route plans"
            description="Select HCPs above to create your first optimized plan."
          />
        )}
        
      </Card>
    </div>
  );
}
