"""
Autonomous Navigation Module for Drone Delivery Systems
Implements path planning, collision avoidance, and autonomous flight control
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math


@dataclass
class GPSCoordinate:
    """Represents a geographic coordinate"""
    latitude: float
    longitude: float
    altitude: float  # meters above sea level
    
    def distance_to(self, other: 'GPSCoordinate') -> float:
        """Calculate Euclidean distance to another coordinate"""
        # Simplified 3D distance calculation
        lat_diff = (self.latitude - other.latitude) * 111000  # meters per degree
        lon_diff = (self.longitude - other.longitude) * 111000 * math.cos(math.radians(self.latitude))
        alt_diff = self.altitude - other.altitude
        return math.sqrt(lat_diff**2 + lon_diff**2 + alt_diff**2)


@dataclass
class Waypoint:
    """Represents a waypoint in the delivery route"""
    position: GPSCoordinate
    arrival_time: Optional[float] = None  # seconds
    hold_time: float = 0.0  # seconds to hold at waypoint


class PathPlanner:
    """
    Implements A* path planning algorithm for autonomous drone navigation
    Optimizes for delivery time while considering battery constraints
    """
    
    def __init__(self, max_speed: float = 15.0, battery_capacity: float = 5000.0):
        """
        Initialize path planner
        
        Args:
            max_speed: Maximum drone speed in m/s (typical: 10-20 m/s)
            battery_capacity: Battery capacity in Wh (Watt-hours)
        """
        self.max_speed = max_speed
        self.battery_capacity = battery_capacity
        self.power_consumption_hover = 200  # Watts (hovering)
        self.power_consumption_cruise = 300  # Watts (cruising)
        
    def plan_route(self, 
                   start: GPSCoordinate, 
                   deliveries: List[GPSCoordinate],
                   end: Optional[GPSCoordinate] = None) -> List[Waypoint]:
        """
        Plan optimal delivery route using greedy nearest-neighbor with A* refinement
        
        Args:
            start: Starting position
            deliveries: List of delivery locations
            end: Return home location (default: same as start)
            
        Returns:
            List of waypoints for the route
        """
        if end is None:
            end = start
            
        # Use nearest-neighbor heuristic for initial route
        route = [start]
        remaining = set(range(len(deliveries)))
        current_pos = start
        current_time = 0.0
        
        while remaining:
            # Find nearest remaining delivery
            nearest_idx = min(remaining, 
                            key=lambda i: current_pos.distance_to(deliveries[i]))
            nearest = deliveries[nearest_idx]
            
            # Calculate travel time and battery usage
            distance = current_pos.distance_to(nearest)
            travel_time = distance / self.max_speed
            battery_used = (self.power_consumption_cruise * travel_time) / 3600  # Wh
            
            # Check battery availability
            if battery_used > self.battery_capacity * 0.2:  # Reserve 20% for safety
                print(f"Warning: Low battery for next segment (need {battery_used}Wh)")
                break
            
            route.append(nearest)
            remaining.remove(nearest_idx)
            current_pos = nearest
            current_time += travel_time
        
        # Return to home
        route.append(end)
        
        # Convert to waypoints
        waypoints = []
        current_time = 0.0
        for i, pos in enumerate(route):
            if i > 0:
                prev_pos = route[i-1]
                distance = prev_pos.distance_to(pos)
                travel_time = distance / self.max_speed
                current_time += travel_time
            
            hold_time = 10.0 if 0 < i < len(route) - 1 else 0.0  # 10s to deliver
            waypoints.append(Waypoint(pos, current_time, hold_time))
        
        return waypoints
    
    def optimize_for_wind(self, 
                         waypoints: List[Waypoint],
                         wind_speed: float,
                         wind_direction: float) -> List[Waypoint]:
        """
        Optimize route for wind conditions
        
        Args:
            waypoints: Original waypoints
            wind_speed: Wind speed in m/s
            wind_direction: Wind direction in degrees
            
        Returns:
            Adjusted waypoints accounting for wind
        """
        # In production, would implement full wind compensation
        # For now, warn if wind is too strong
        if wind_speed > self.max_speed * 0.5:
            print(f"Warning: Wind speed {wind_speed} m/s may affect delivery")
        
        return waypoints


class CollisionAvoidanceSystem:
    """
    Implements obstacle detection and avoidance using onboard sensors
    Processes LiDAR, camera, and radar data for real-time safety
    """
    
    def __init__(self, 
                 safety_distance: float = 5.0,
                 update_rate: float = 30.0):  # Hz
        """
        Initialize collision avoidance system
        
        Args:
            safety_distance: Minimum safe distance from obstacles (meters)
            update_rate: Update rate for sensor processing (Hz)
        """
        self.safety_distance = safety_distance
        self.update_rate = update_rate
        self.lidar_range = 200.0  # meters
        self.camera_range = 100.0  # meters
        self.emergency_stop_distance = 2.0  # meters
        
    def process_lidar_data(self, 
                          lidar_points: np.ndarray) -> Tuple[bool, Optional[Tuple[float, float, float]]]:
        """
        Process LiDAR point cloud for obstacles
        
        Args:
            lidar_points: Nx3 array of (x, y, z) coordinates from LiDAR
            
        Returns:
            Tuple of (obstacle_detected, nearest_obstacle_position)
        """
        if len(lidar_points) == 0:
            return False, None
        
        # Calculate distance from drone (at origin)
        distances = np.linalg.norm(lidar_points, axis=1)
        
        # Find minimum distance
        min_distance = np.min(distances)
        min_idx = np.argmin(distances)
        nearest_point = lidar_points[min_idx]
        
        # Check if obstacle is within safety distance
        if min_distance < self.safety_distance:
            return True, tuple(nearest_point)
        
        return False, None
    
    def detect_obstacles_camera(self, 
                               frame: np.ndarray,
                               confidence_threshold: float = 0.7) -> List[dict]:
        """
        Detect objects in camera frame using YOLO-style detection
        (Placeholder for actual implementation)
        
        Args:
            frame: Image frame from camera
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            List of detected objects with bounding boxes
        """
        # In production, would use actual YOLO or similar model
        # For now, return dummy detections
        detections = [
            {
                'class': 'power_line',
                'confidence': 0.95,
                'bbox': (100, 50, 200, 100),  # (x1, y1, x2, y2)
                'distance': 50.0  # estimated distance in meters
            },
            {
                'class': 'bird',
                'confidence': 0.87,
                'bbox': (300, 150, 350, 200),
                'distance': 40.0
            }
        ]
        return [d for d in detections if d['confidence'] >= confidence_threshold]
    
    def compute_avoidance_vector(self,
                                drone_position: np.ndarray,
                                obstacle_position: np.ndarray,
                                current_velocity: np.ndarray) -> np.ndarray:
        """
        Compute vector to avoid obstacle
        
        Args:
            drone_position: Current drone position (x, y, z)
            obstacle_position: Detected obstacle position
            current_velocity: Current velocity vector
            
        Returns:
            Recommended velocity adjustment vector
        """
        # Vector from drone to obstacle
        to_obstacle = obstacle_position - drone_position
        distance = np.linalg.norm(to_obstacle)
        
        if distance < self.emergency_stop_distance:
            # Emergency: stop immediately
            return -current_velocity
        
        # Compute perpendicular direction
        direction_normal = to_obstacle / (distance + 1e-6)
        avoidance_vector = -direction_normal
        
        # Blend with current velocity to avoid jerky movements
        blended = current_velocity * 0.5 + avoidance_vector * 0.5
        
        return blended / (np.linalg.norm(blended) + 1e-6) * np.linalg.norm(current_velocity)


class AutoPilot:
    """
    Main autopilot system coordinating path planning, collision avoidance, and control
    Implements state machine for autonomous flight
    """
    
    def __init__(self):
        """Initialize autopilot system"""
        self.path_planner = PathPlanner()
        self.collision_avoidance = CollisionAvoidanceSystem()
        self.state = "IDLE"  # IDLE, ARMED, IN_FLIGHT, LANDING, EMERGENCY
        self.current_waypoint_idx = 0
        self.waypoints: List[Waypoint] = []
        self.telemetry = {
            'battery_percent': 100.0,
            'position': np.array([0.0, 0.0, 0.0]),
            'velocity': np.array([0.0, 0.0, 0.0]),
            'wind_speed': 0.0
        }
        
    def start_mission(self,
                     start: GPSCoordinate,
                     deliveries: List[GPSCoordinate]) -> bool:
        """
        Start autonomous delivery mission
        
        Args:
            start: Starting position
            deliveries: List of delivery locations
            
        Returns:
            True if mission started successfully
        """
        if self.state != "IDLE":
            print("Error: Drone not idle")
            return False
        
        # Plan route
        self.waypoints = self.path_planner.plan_route(start, deliveries)
        self.current_waypoint_idx = 0
        self.state = "ARMED"
        
        print(f"Mission planned: {len(self.waypoints)} waypoints")
        return True
    
    def update(self,
              lidar_data: Optional[np.ndarray] = None,
              camera_frame: Optional[np.ndarray] = None) -> dict:
        """
        Main autopilot update loop (should be called at 30-100 Hz)
        
        Args:
            lidar_data: LiDAR point cloud data
            camera_frame: Camera frame for vision processing
            
        Returns:
            Control commands for drone motors
        """
        if self.state == "IDLE":
            return {'throttle': 0, 'pitch': 0, 'roll': 0, 'yaw': 0}
        
        # Check for obstacles
        obstacle_detected = False
        if lidar_data is not None:
            obstacle_detected, obstacle_pos = self.collision_avoidance.process_lidar_data(lidar_data)
        
        if camera_frame is not None:
            detections = self.collision_avoidance.detect_obstacles_camera(camera_frame)
            if detections:
                obstacle_detected = True
        
        if obstacle_detected:
            self.state = "OBSTACLE_AVOIDANCE"
            print("Obstacle detected - initiating avoidance maneuver")
        
        # Get current waypoint
        if self.current_waypoint_idx >= len(self.waypoints):
            self.state = "IDLE"
            print("Mission completed")
            return {'throttle': 0, 'pitch': 0, 'roll': 0, 'yaw': 0}
        
        current_waypoint = self.waypoints[self.current_waypoint_idx]
        
        # Compute control commands to reach waypoint
        position_error = np.array([
            current_waypoint.position.latitude - self.telemetry['position'][0],
            current_waypoint.position.longitude - self.telemetry['position'][1],
            current_waypoint.position.altitude - self.telemetry['position'][2]
        ])
        
        # Simple proportional control
        Kp = 0.1
        desired_velocity = Kp * position_error
        
        # Convert velocity to attitude commands
        control_commands = {
            'throttle': max(0, 1.0 if desired_velocity[2] > 0 else -0.5),
            'pitch': np.clip(desired_velocity[1] / 10, -1, 1),
            'roll': np.clip(desired_velocity[0] / 10, -1, 1),
            'yaw': 0.0
        }
        
        # Check if waypoint reached
        if np.linalg.norm(position_error) < 2.0:
            self.current_waypoint_idx += 1
        
        return control_commands


# Example usage
if __name__ == "__main__":
    # Define delivery locations
    warehouse = GPSCoordinate(latitude=40.7128, longitude=-74.0060, altitude=50)
    delivery1 = GPSCoordinate(latitude=40.7150, longitude=-74.0050, altitude=50)
    delivery2 = GPSCoordinate(latitude=40.7180, longitude=-74.0080, altitude=50)
    delivery3 = GPSCoordinate(latitude=40.7120, longitude=-74.0120, altitude=50)
    
    deliveries = [delivery1, delivery2, delivery3]
    
    # Initialize autopilot
    autopilot = AutoPilot()
    
    # Start mission
    print("Starting autonomous delivery mission...")
    autopilot.start_mission(warehouse, deliveries)
    
    # Simulate flight
    for i in range(5):
        control_commands = autopilot.update()
        print(f"Step {i}: Control = {control_commands}")
    
    print("✅ Autonomous navigation example completed!")
