from ip2geotools.databases.noncommercial import DbIpCity
from geopy.geocoders import Nominatim

# def my_middleware(get_response):
#     print("Inside My_Middleware")
#     def my_function(request):
#         print("Inside myFunction")
#         response = get_response(request)
#         print("after view")
#         return response
#     return my_function


def printDetails(ip):
    res = DbIpCity.get(ip, api_key="free")
    print(f"IP Address: {res.ip_address}")
    # print(f"Location: {res.city}, {res.region}, {res.country}")
    print(f"Coordinates: (Lat: {res.latitude}, Lng: {res.longitude})")

    latitude = res.latitude
    longitude = res.longitude

    geoLoc = Nominatim(user_agent = "GetLoc")
    locname = geoLoc.reverse(f'{latitude},{longitude}')
    print(locname.address)

class MyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        print("One time initialization")
    def __call__(self, request):
        print("This is before calling view")

        response = self.get_response(request)
        # print("Response", response)
        user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        print(user_ip_address)
        if user_ip_address:
            ip = user_ip_address.split(',')[0]
            print("inside if middleware")
        else:
            print("inside else middleware")
            ip = request.META.get('REMOTE_ADDR')
        printDetails(ip)
        print("This is after view")
        return response
