import boto3
import os
import pyproj

def get_s3():
    return boto3.resource(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_ACCESS_SECRET"),
        config=boto3.session.Config(signature_version="s3v4"),
    )

def get_projs(user_projs=[]):
    """
    Retrieve a serializable list of pyproj supported codes. Currently supported are all UTM zones and Latitude-longitude
    user_projs are additional projections requested by user in epsg code integer format
    """
    utm = range(32601, 32661) + range(32701, 32761)
    latlong = [4326]
    others = [28992, ]  # dutch Rijksdriehoek
    all_codes = user_projs + latlong + utm + others
    crs_list = [{"epsg": code, "name": pyproj.CRS.from_epsg(code).name} for code in all_codes]
    return crs_list