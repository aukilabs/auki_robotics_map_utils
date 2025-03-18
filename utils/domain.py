from .http_utils import send_request, send_files
import json
import re
import base64
from PIL import Image
import io
import yaml
import math
import traceback

class Domain:
    def __init__(self, domain_config):
        """
        Initialize the Domain object.
        
        :param domain_config: dict type that contains domain configurations.
        """
        self.domain_id = domain_config["domain_id"]
        self.account = domain_config["posemesh_account"]
        self.password = domain_config["posemesh_password"]
        self.map_endpoint = domain_config["map_endpoint"]
        self.raycast_endpoint = domain_config["raycast_endpoint"]
        self.navmesh_endpoint = domain_config["navmesh_endpoint"]
        self.routing_endpoint = domain_config["routing_endpoint"]
        
        self._posemesh_token = ''
        self._dds_token = ''
        self._domain_info = {}
        self._domain_server = None

    def auth(self):
        # Auth User Posemesh
        url1 = "https://api.posemesh.org/user/login"
        headers1 = {'Content-Type': 'application/json',
                    'Accept': 'application/json'}
        body1 = {'email': self.account,
                 'password': self.password}
        
        ret1, response1 = send_request('POST', url1, headers1, body1)
        if not ret1:
            return False, 'Failed to authenticate posemesh account'
        rep_json1 = json.loads(response1.text)
        self._posemesh_token = rep_json1['access_token']

        # Auth DDS
        url2 = "https://api.posemesh.org/service/domains-access-token"
        headers2 = {'Accept': 'application/json',
                    'Authorization': f"Bearer {self._posemesh_token}"}
        ret2, response2 = send_request('POST', url2, headers2)
        if not ret2:
            return False, 'Failed to authenticate domain dds'
        rep_json2 = json.loads(response2.text)
        self._dds_token = rep_json2['access_token']

        # Auth Domain
        url3 = f"https://dds.posemesh.org/api/v1/domains/{self.domain_id}/auth"
        headers3 = {'Accept': 'application/json',
                    'Authorization': f"Bearer {self._dds_token}"}
        ret3, response3 = send_request('POST', url3, headers3)
        if not ret3:
            return False, 'Failed to authenticate domain access'
        self._domain_info = json.loads(response3.text)
        self._domain_server = self._domain_info["domain_server"]["url"]

        return True, ''

    def get_map(self, image_format="png", resolution=20):
        method = 'POST'
        
        url = self.map_endpoint
        headers = {'authorization': f'Bearer {self._domain_info["access_token"]}'}  

        print("image_format: ", image_format)

        # Use the requested format directly - server can handle stcm
        image_format_request = image_format
        
        # For PGM, we still need to request PNG and convert
        if image_format == "pgm":
            image_format_request = "png"

        body = {
            'domainId': self.domain_id,
            'domainServerUrl': self._domain_server,
            'height': 0.1,
            'fileType': image_format_request,
            'pixelsPerMeter': resolution
        }

        success, response = send_request(method, url, headers, body)

        # For STCM format, handle the binary response directly
        if image_format == "stcm":
            try:
                # The response is a multipart form, we need to extract just the STCM data
                content_type = response.headers.get('Content-Type', '')
                print(f"Content-Type: {content_type}")
                if 'multipart/form-data' in content_type:
                    # Get the boundary from the Content-Type header
                    boundary = content_type.split('boundary=')[1].strip()
                    boundary = f'--{boundary}'
                    print(f"Boundary: {boundary}")
                    
                    # Split the data using the boundary marker
                    parts = response.content.split(boundary.encode())
                    print(f"Number of parts: {len(parts)}")
                    
                    # Find the part containing the STCM data
                    stcm_data = None
                    for i, part in enumerate(parts):
                        print(f"\nPart {i} first 100 bytes: {part[:100]}")
                        if b'name="img"' in part:
                            print(f"Found img part in part {i}")
                            # Find the double newline that separates headers from content
                            header_end = part.find(b'\r\n\r\n')
                            if header_end > 0:
                                # Extract the base64 encoded data after the header
                                base64_data = part[header_end + 4:].strip()
                                print(f"Raw base64 length: {len(base64_data)}")
                                
                                # The data is base64 encoded, decode it to get the actual binary STCM data
                                try:
                                    # Clean up any whitespace or newlines that might be in the base64 string
                                    clean_base64 = re.sub(b'[\\s\\r\\n]', b'', base64_data)
                                    print(f"Cleaned base64 length: {len(clean_base64)}")
                                    # Decode the base64 data
                                    stcm_data = base64.b64decode(clean_base64)
                                    print(f"Decoded data length: {len(stcm_data)}")
                                except Exception as e:
                                    print(f"Failed to decode base64 data: {e}")
                                    traceback.print_exc()
                                break
                    
                    if stcm_data:
                        # Save the raw STCM data
                        with open(f"map.{image_format}", "wb") as stcm_file:
                            stcm_file.write(stcm_data)
                        print(f"STCM data saved as map.{image_format}")
                    else:
                        print("Failed to extract STCM data from response")
                else:
                    # If not multipart, assume the entire content is base64 encoded STCM data
                    try:
                        # Clean up any whitespace or newlines
                        clean_data = re.sub(b'[\\s\\r\\n]', b'', response.content)
                        # Decode the base64 data
                        stcm_data = base64.b64decode(clean_data)
                    except Exception as e:
                        print(f"Failed to decode base64 data: {e}")
                        traceback.print_exc()
                        # If decoding fails, use the raw content
                        stcm_data = response.content
                    
                    with open(f"map.{image_format}", "wb") as stcm_file:
                        stcm_file.write(stcm_data)
                    print(f"STCM data saved as map.{image_format}")
                
                return
            except Exception as e:
                print(f"Failed to save STCM data: {e}")
                traceback.print_exc()  # Print the full exception traceback for debugging
                return

        # For other formats, continue with the existing processing
        raw_data = response.text

        # Split the data using the boundary marker
        boundary = raw_data.split("\n", 1)[0].strip()
        parts = raw_data.split(boundary)

        # Initialize placeholders for the image and YAML data
        image_data = None
        yaml_data = None

        # Iterate through each part of the form-data
        for part in parts:
            if 'name="img"' in part:
                # Extract and decode the base64 image data, handle newlines
                image_data_match = re.search(r'name="img"\s*\n([a-zA-Z0-9+/=\n]+)', part)
                if image_data_match:
                    # Remove any newlines or spaces in the base64-encoded data
                    encoded_image = "".join(image_data_match.group(1).splitlines())
                    image_data = base64.b64decode(encoded_image)
            elif "name=\"yaml\"" in part:
                # Extract the YAML content
                yaml_data_match = re.search(r"name=\"yaml\"\s*\n(.+)", part, re.DOTALL)
                if yaml_data_match:
                    yaml_data = yaml_data_match.group(1).strip()

        # Save the image data in the specified format
        image_filename = f"map.{image_format}"  # Determine the file name dynamically
        if image_data:
            try:
                image = Image.open(io.BytesIO(image_data))
                if image_format == "png":
                    image.save(image_filename, "PNG")
                elif image_format == "bmp":
                    image.convert("RGB").save(image_filename, "BMP")  # Ensure RGB for 24-bit BMP
                elif image_format == "pgm":
                    image = image.convert("L")  # Convert to grayscale
                    width, height = image.size

                    # Create a binary occupancy grid: 0 (free/black), 255 (occupied/white), 128 (unknown/gray)
                    binary_grid = []
                    for pixel in image.getdata():
                        if pixel > 165:  # Occupied threshold (65% of 255)
                            binary_grid.append(255)  # Occupied (white)
                        elif pixel < 50:  # Free threshold (19.6% of 255)
                            binary_grid.append(0)  # Free (black)
                        else:
                            binary_grid.append(128)  # Unknown (gray)

                    # Save the binary occupancy grid as a PGM file
                    with open(image_filename, "w") as pgm_file:
                        pgm_file.write(f"P2\n{width} {height}\n255\n")
                        pgm_file.write("\n".join(
                            " ".join(map(str, binary_grid[i:i + width])) for i in range(0, len(binary_grid), width)))

                print(f"Image saved as {image_filename}")
            except Exception as e:
                print(f"Failed to save image in {image_format} format: {e}")
        else:
            print("Image data not found or could not be saved.")

        # Update the YAML file to reference the correct image file
        if yaml_data:
            try:
                yaml_dict = yaml.safe_load(yaml_data)
                yaml_dict['image'] = image_filename  # Update the image field
                
                # If the requested format is pgm but we received png from the server,
                # ensure the yaml file references the pgm file
                if image_format == "pgm" and 'image_format' in yaml_dict:
                    yaml_dict['image_format'] = 'pgm'
                
                with open("map.yaml", "w") as yaml_file:
                    yaml.dump(yaml_dict, yaml_file)
                print("Updated YAML saved as map.yaml")
            except Exception as e:
                print(f"Failed to save updated YAML: {e}")
        else:
            print("YAML data not found or could not be saved.")

    def get_raycast(self, pose):
        method = 'POST'

        url = self.raycast_endpoint
        headers = {'authorization': f'Bearer {self._domain_info["access_token"]}'}

        body = {
            'domainId': self.domain_id,
            'domainServerUrl': self._domain_server,
            'ray': pose
        }

        success, raycast = send_request(method, url, headers, body)

        if not success:
            return False, "Failed to send raycast to domain"

        # Assuming the response is in JSON format
        try:
            raycast_data = raycast.json()  # Parse the JSON response
            print(raycast_data)
        except ValueError as e:
            return False, f"Failed to parse response JSON: {e}"

        return True, raycast_data
    
    def get_navmesh_coord(self, coords):
        method = 'POST'
        url = self.navmesh_endpoint
        headers = {'authorization': f'Bearer {self._domain_info["access_token"]}'}

        body = {
            'domainId': self.domain_id,
            'domainServerUrl': self._domain_server,
            'target': coords,
            'radius': 0.5
        }

        success, response = send_request(method, url, headers, body)

        if not success:
            return False, "Failed to get navmesh coord"

        print(response.json())
        
        x1 = coords['x']
        z1 = coords['z']
        x2 = response.json()['restricted']['x']
        z2 = response.json()['restricted']['z']

        delta_x = x1 - x2
        delta_z = z1 - z2

        z2 = -abs(z2) if z2 > 0 else abs(z2)
        yaw = round(math.atan2(delta_z, delta_x), 2)  # Result in radians, rounded to 2 decimal places
        yaw = -abs(yaw) if yaw > 0 else abs(yaw)
        pose = {'x': x2, 'z': z2, 'yaw': yaw}

        return pose
    

    def optimize_route(self, waypoints):
        method = 'POST'
        url = self.routing_endpoint
        headers = {'authorization': f'Bearer {self._domain_info["access_token"]}'}

        body = {
            'domainServerUrl': self._domain_server,
            'domainId': self.domain_id,
            'wayPoints': waypoints,
            'radius': 0.5,
            'optimizeRoute': True
        }

        success, response = send_request(method, url, headers, body)

        if not success:
            return None, None

        response_data = response.json()
        if 'waypointIndices' not in response_data or 'waypoints' not in response_data:
            return None, None

        # Get the sorted original waypoints
        sorted_original = [waypoints[i] for i in response_data['waypointIndices']]
        
        # Get the sorted on-mesh coordinates
        sorted_onmesh = []
        for i in response_data['waypointIndices']:
            # Find the corresponding waypoint in the response
            for wp in response_data['waypoints']:
                if wp['original'] == waypoints[i]:
                    sorted_onmesh.append(wp['adjusted'])
                    break

        return sorted_original, sorted_onmesh