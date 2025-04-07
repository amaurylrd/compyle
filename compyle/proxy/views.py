# from django.http import JsonResponse
# from django.views import View
# from apiwrapper.services.dispatcher import dispatch_request

# class DynamicAPIProxyView(View):
#     def get(self, request, *args, **kwargs):
#         path_parts = request.path.strip("/").split("/")
#         if len(path_parts) < 2:
#             return JsonResponse({"error": "Invalid route"}, status=400)

#         service, endpoint = path_parts[:2]
#         query_params = request.GET.dict()
#         status, data = dispatch_request(service, endpoint, query_params)
#         return JsonResponse(data, status=status)