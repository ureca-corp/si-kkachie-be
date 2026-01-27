# Route Search

## Overview

Kkachie integrates with Naver Maps Directions API to provide route search functionality. Users can find routes with optional waypoints and view their search history.

## Route Options

| Option | Korean | Description |
|--------|--------|-------------|
| traoptimal | 실시간 최적 | Real-time optimal route |
| trafast | 실시간 빠른길 | Fastest route |
| tracomfort | 실시간 편한길 | Most comfortable route |
| traavoidtoll | 무료 우선 | Toll-free priority |
| traavoidcaronly | 자동차 전용도로 회피 | Avoid car-only roads |

## User Flow Diagram

```
+-------------------+
|  Route Search     |
+--------+----------+
         |
         v
+-------------------+
|  Enter Start      |
|  + End Location   |
|  + Waypoints (opt)|
+--------+----------+
         |
         v
+-------------------+
| Select Option     |
| (optimal/fast/..) |
+--------+----------+
         |
         v
+-------------------+
| POST /routes/     |
| search            |
+--------+----------+
         |
         v
+-------------------+
|  Route Result     |
|  - Distance       |
|  - Duration       |
|  - Map Path       |
+--------+----------+
         |
         v (auto-save)
+-------------------+
|  Route History    |
+-------------------+
```

## Screen Mockups

### Route Search Screen
```
+---------------------------+
|  <  Find Route            |
+---------------------------+
|                           |
|  From:                    |
|  +------------------------+
|  | Seoul Station          |
|  +------------------------+
|                           |
|  To:                      |
|  +------------------------+
|  | Gangnam Station        |
|  +------------------------+
|                           |
|  + Add waypoint           |
|                           |
|  Route Option:            |
|  [v] Optimal              |
|  [ ] Fastest              |
|  [ ] Comfortable          |
|  [ ] Toll-free            |
|                           |
|  +-------------------+    |
|  |   Search Route    |    |
|  +-------------------+    |
|                           |
+---------------------------+
```

### Route Result Screen
```
+---------------------------+
|  <  Route                 |
+---------------------------+
|                           |
|  +------------------------+
|  |                       ||
|  |      [MAP VIEW]       ||
|  |                       ||
|  |  A -----> B           ||
|  |                       ||
|  +------------------------+
|                           |
|  Seoul Station            |
|       |                   |
|       | 12.5 km           |
|       | ~30 min           |
|       v                   |
|  Gangnam Station          |
|                           |
|  +-------------------+    |
|  |  Open in Naver    |    |
|  +-------------------+    |
|                           |
+---------------------------+
```

### Route History Screen
```
+---------------------------+
|  <  Recent Routes         |
+---------------------------+
|                           |
| Today                     |
| +------------------------+|
| | Seoul Stn -> Gangnam   ||
| | 12.5 km | 30 min       ||
| | 10:30 AM               ||
| +------------------------+|
|                           |
| +------------------------+|
| | Myeongdong -> Hongdae  ||
| | 8.2 km | 22 min        ||
| | 9:15 AM                ||
| +------------------------+|
|                           |
| Yesterday                 |
| +------------------------+|
| | Airport -> Seoul Stn   ||
| | 58.3 km | 1h 15min     ||
| | 3:45 PM                ||
| +------------------------+|
|                           |
+---------------------------+
```

## API Endpoints

### 1. Search Route (POST /routes/search)

Searches for a route between two points with optional waypoints.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/routes/search" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "start": {
      "name": "Seoul Station",
      "lat": 37.5547,
      "lng": 126.9706
    },
    "end": {
      "name": "Gangnam Station",
      "lat": 37.4979,
      "lng": 127.0276
    },
    "waypoints": [
      {
        "name": "Myeongdong",
        "lat": 37.5636,
        "lng": 126.9869
      }
    ],
    "option": "traoptimal"
  }'
```

**Request Body:**
```typescript
interface PointRequest {
  name: string;
  lat: number;   // -90 to 90
  lng: number;   // -180 to 180
}

interface RouteSearchRequest {
  start: PointRequest;
  end: PointRequest;
  waypoints?: PointRequest[];  // Max 5 waypoints
  option?: RouteOption;        // Default: "traoptimal"
}

type RouteOption =
  | "traoptimal"
  | "trafast"
  | "tracomfort"
  | "traavoidtoll"
  | "traavoidcaronly";
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "경로 검색에 성공했어요",
  "data": {
    "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
    "start": {
      "name": "Seoul Station",
      "lat": 37.5547,
      "lng": 126.9706
    },
    "end": {
      "name": "Gangnam Station",
      "lat": 37.4979,
      "lng": 127.0276
    },
    "total_distance_m": 12500,
    "total_duration_s": 1800,
    "distance_text": "12.5km",
    "duration_text": "약 30분",
    "path": [
      {"lat": 37.5547, "lng": 126.9706},
      {"lat": 37.5500, "lng": 126.9800},
      {"lat": 37.5200, "lng": 127.0000},
      {"lat": 37.4979, "lng": 127.0276}
    ]
  }
}
```

---

### 2. Get Recent Routes (GET /routes/recent)

Returns user's recent route searches.

**Request:**
```bash
curl -X GET "https://api.kkachie.com/routes/recent?limit=10" \
  -H "Authorization: Bearer {token}"
```

**Query Parameters:**
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| limit | number | 10 | 50 | Number of routes to return |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": [
    {
      "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
      "start_name": "Seoul Station",
      "end_name": "Gangnam Station",
      "total_distance_m": 12500,
      "total_duration_s": 1800,
      "created_at": "2026-01-27T10:30:00Z"
    },
    {
      "id": "018d5c4f-yyyy-7yyy-yyyy-yyyyyyyyyyyy",
      "start_name": "Myeongdong",
      "end_name": "Hongdae",
      "total_distance_m": 8200,
      "total_duration_s": 1320,
      "created_at": "2026-01-27T09:15:00Z"
    }
  ]
}
```

## TypeScript Types

```typescript
// Route Options
type RouteOption =
  | "traoptimal"
  | "trafast"
  | "tracomfort"
  | "traavoidtoll"
  | "traavoidcaronly";

// Point (Request/Response)
interface PointRequest {
  name: string;
  lat: number;
  lng: number;
}

interface PointResponse {
  name: string;
  lat: number;
  lng: number;
}

// Route Search Request
interface RouteSearchRequest {
  start: PointRequest;
  end: PointRequest;
  waypoints?: PointRequest[];
  option?: RouteOption;
}

// Route Search Response
interface RouteSearchResponse {
  id: string;
  start: PointResponse;
  end: PointResponse;
  total_distance_m: number;
  total_duration_s: number;
  distance_text: string;
  duration_text: string;
  path: Array<{ lat: number; lng: number }>;
}

// Route History Response
interface RouteHistoryResponse {
  id: string;
  start_name: string;
  end_name: string;
  total_distance_m: number;
  total_duration_s: number;
  created_at: string;
}
```

## React Native Implementation Example

```typescript
import MapView, { Polyline, Marker } from 'react-native-maps';

// Search Route
async function searchRoute(
  start: PointRequest,
  end: PointRequest,
  waypoints?: PointRequest[],
  option: RouteOption = 'traoptimal'
): Promise<RouteSearchResponse> {
  return apiClient<RouteSearchResponse>('/routes/search', {
    method: 'POST',
    body: JSON.stringify({
      start,
      end,
      waypoints,
      option,
    }),
  });
}

// Get Recent Routes
async function getRecentRoutes(
  limit: number = 10
): Promise<RouteHistoryResponse[]> {
  return apiClient<RouteHistoryResponse[]>(`/routes/recent?limit=${limit}`);
}

// Format Distance
function formatDistance(meters: number): string {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(1)}km`;
  }
  return `${meters}m`;
}

// Format Duration
function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (hours > 0) {
    return `${hours}h ${minutes}min`;
  }
  return `${minutes} min`;
}

// Route Map Component
function RouteMap({ route }: { route: RouteSearchResponse }) {
  const coordinates = route.path.map((p) => ({
    latitude: p.lat,
    longitude: p.lng,
  }));

  const region = {
    latitude: (route.start.lat + route.end.lat) / 2,
    longitude: (route.start.lng + route.end.lng) / 2,
    latitudeDelta: Math.abs(route.start.lat - route.end.lat) * 1.5,
    longitudeDelta: Math.abs(route.start.lng - route.end.lng) * 1.5,
  };

  return (
    <MapView style={styles.map} region={region}>
      <Marker
        coordinate={{ latitude: route.start.lat, longitude: route.start.lng }}
        title={route.start.name}
        pinColor="green"
      />
      <Marker
        coordinate={{ latitude: route.end.lat, longitude: route.end.lng }}
        title={route.end.name}
        pinColor="red"
      />
      <Polyline
        coordinates={coordinates}
        strokeWidth={4}
        strokeColor="#4A90D9"
      />
    </MapView>
  );
}

// Route Search Screen
function RouteSearchScreen() {
  const [start, setStart] = useState<PointRequest | null>(null);
  const [end, setEnd] = useState<PointRequest | null>(null);
  const [waypoints, setWaypoints] = useState<PointRequest[]>([]);
  const [option, setOption] = useState<RouteOption>('traoptimal');
  const [route, setRoute] = useState<RouteSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!start || !end) return;

    setLoading(true);
    try {
      const result = await searchRoute(
        start,
        end,
        waypoints.length > 0 ? waypoints : undefined,
        option
      );
      setRoute(result);
    } catch (error) {
      alert('Route search failed');
    } finally {
      setLoading(false);
    }
  };

  const addWaypoint = (point: PointRequest) => {
    if (waypoints.length < 5) {
      setWaypoints([...waypoints, point]);
    }
  };

  return (
    <View>
      <LocationPicker
        label="From"
        value={start}
        onChange={setStart}
      />
      <LocationPicker
        label="To"
        value={end}
        onChange={setEnd}
      />

      {waypoints.map((wp, index) => (
        <View key={index}>
          <Text>Waypoint {index + 1}: {wp.name}</Text>
          <TouchableOpacity onPress={() => {
            setWaypoints(waypoints.filter((_, i) => i !== index));
          }}>
            <Text>Remove</Text>
          </TouchableOpacity>
        </View>
      ))}

      {waypoints.length < 5 && (
        <TouchableOpacity onPress={() => {/* Add waypoint picker */}}>
          <Text>+ Add Waypoint</Text>
        </TouchableOpacity>
      )}

      <RouteOptionPicker value={option} onChange={setOption} />

      <Button
        title="Search Route"
        onPress={handleSearch}
        disabled={!start || !end || loading}
      />

      {route && (
        <View>
          <RouteMap route={route} />
          <Text>{route.distance_text}</Text>
          <Text>{route.duration_text}</Text>
        </View>
      )}
    </View>
  );
}
```

## Location Picker Integration

For selecting locations, you can integrate with:

1. **Device GPS**: Get current location
2. **Place Search**: Use Naver or Google Places API
3. **Map Selection**: Let user tap on map to select point

```typescript
import * as Location from 'expo-location';

// Get Current Location
async function getCurrentLocation(): Promise<PointRequest> {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') {
    throw new Error('Location permission denied');
  }

  const location = await Location.getCurrentPositionAsync({});
  const address = await Location.reverseGeocodeAsync({
    latitude: location.coords.latitude,
    longitude: location.coords.longitude,
  });

  return {
    name: address[0]?.name || 'Current Location',
    lat: location.coords.latitude,
    lng: location.coords.longitude,
  };
}
```

## Error Handling

| Status Code | Error Status | Message | Action |
|-------------|--------------|---------|--------|
| 400 | ERROR_ROUTE_NOT_FOUND | 경로를 찾을 수 없어요 | Check coordinates |
| 400 | ERROR_TOO_MANY_WAYPOINTS | 경유지는 최대 5개까지 가능해요 | Reduce waypoints |
| 422 | VALIDATION_FAILED | (varies) | Check coordinate ranges |

## Best Practices

1. **Coordinate Validation**: Validate lat/lng ranges before API call
2. **Waypoint Limit**: Clearly show max 5 waypoints limit
3. **Loading State**: Show map loading skeleton while searching
4. **Route Caching**: Cache recent routes for quick re-access
5. **Deep Linking**: Support opening results in Naver Maps app
6. **Offline Handling**: Save route path for offline viewing
7. **History Management**: Allow users to delete unwanted history entries

## Opening in Native Maps

```typescript
import { Linking, Platform } from 'react-native';

async function openInNaverMaps(
  start: PointResponse,
  end: PointResponse
): Promise<void> {
  const scheme = Platform.select({
    ios: 'nmap://',
    android: 'nmap://',
  });

  const url = `${scheme}route/car?slat=${start.lat}&slng=${start.lng}&sname=${encodeURIComponent(start.name)}&dlat=${end.lat}&dlng=${end.lng}&dname=${encodeURIComponent(end.name)}&appname=com.kkachie.app`;

  const canOpen = await Linking.canOpenURL(url);

  if (canOpen) {
    await Linking.openURL(url);
  } else {
    // Fallback to web
    const webUrl = `https://map.naver.com/v5/directions/${start.lng},${start.lat},${encodeURIComponent(start.name)}/${end.lng},${end.lat},${encodeURIComponent(end.name)}/-/car`;
    await Linking.openURL(webUrl);
  }
}
```
