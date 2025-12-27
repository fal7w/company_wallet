# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import json
import math
from frappe.utils import flt
from frappe import _


EARTH_RADIUS = 6378137

# TODO: rename doctype to Wallet Service Location 
class CompanyLocation(Document):
	def validate(self):
		self.calculate_location_area()

	def calculate_location_area(self):
		features = self.get_location_features()
		new_area = compute_area(features)

		self.area_difference = new_area - flt(self.area)
		self.area = new_area

	def get_location_features(self):
		if not self.location:
			return []

		features = json.loads(self.location).get("features")

		if not isinstance(features, list):
			features = json.loads(features)
		return features

	def set_location_features(self, features):
		if not self.location:
			self.location = '{"type":"FeatureCollection","features":[]}'

		location = json.loads(self.location)
		location["features"] = features

		self.db_set("location", json.dumps(location), commit=True)


def compute_area(features):
	"""
	Calculate the total area for a set of location features.
	Reference from https://github.com/scisco/area.

	Args:
		`features` (list of dict): Features marked on the map as
		GeoJSON data

	Returns:
			float: The approximate signed geodesic area (in sq. meters)
	"""

	layer_area = 0.0

	for feature in features:
		feature_type = feature.get("geometry", {}).get("type")

		if feature_type == "Polygon":
			layer_area += _polygon_area(coords=feature.get("geometry").get("coordinates"))
		elif feature_type == "Point" and feature.get("properties").get("point_type") == "circle":
			layer_area += math.pi * math.pow(feature.get("properties").get("radius"), 2)
	return layer_area


def _polygon_area(coords):
	if not coords:
		return 0

	area = abs(_ring_area(coords[0]))

	for i in range(1, len(coords)):
		area -= abs(_ring_area(coords[i]))

	return area


def _ring_area(coords):
	area = 0.0
	coords_length = len(coords)

	if coords_length > 2:
		for i in range(coords_length):
			if i == coords_length - 2:  # i = N-2
				lower_index = coords_length - 2
				middle_index = coords_length - 1
				upper_index = 0
			elif i == coords_length - 1:  # i = N-1
				lower_index = coords_length - 1
				middle_index = 0
				upper_index = 1
			else:  # i = 0 to N-3
				lower_index = i
				middle_index = i + 1
				upper_index = i + 2

			p1 = coords[lower_index]
			p2 = coords[middle_index]
			p3 = coords[upper_index]
			area += (math.radians(p3[0]) - math.radians(p1[0])) * math.sin(math.radians(p2[1]))

		area = area * EARTH_RADIUS * EARTH_RADIUS / 2
	return area
