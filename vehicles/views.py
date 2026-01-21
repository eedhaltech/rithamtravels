from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vehicle.objects.filter(is_available=True, is_active=True)
    serializer_class = VehicleSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """
        Optionally filter vehicles based on query parameters
        """
        queryset = Vehicle.objects.filter(is_available=True, is_active=True)
        
        # Get query parameters
        trip_type = self.request.query_params.get('trip_type', None)
        total_distance = self.request.query_params.get('total_distance', None)
        total_days = self.request.query_params.get('total_days', None)
        pickup_city = self.request.query_params.get('pickup_city', None)
        
        # For now, we'll just return all available vehicles
        # In the future, you can add filtering logic based on these parameters
        # For example:
        # if trip_type:
        #     queryset = queryset.filter(vehicle_tariffs__trip_type=trip_type)
        # if total_distance:
        #     # Filter based on distance requirements
        #     pass
        
        return queryset.order_by('fare_per_km')
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to add calculated pricing information
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Get query parameters for calculations
        trip_type = request.query_params.get('trip_type', 'round')
        total_distance = float(request.query_params.get('total_distance', 0))
        total_days = int(request.query_params.get('total_days', 1))
        
        # Add calculated fields to each vehicle
        results = []
        for vehicle_data in serializer.data:
            vehicle = queryset.get(id=vehicle_data['id'])
            
            # Calculate total amount based on trip type
            if trip_type == 'round':
                # Round Trip: Day-based calculation
                vehicle_fee = total_days * float(vehicle.per_day_fee)
                driver_charge = total_days * float(vehicle.driver_charge_per_day)
                total_amount = vehicle_fee + driver_charge
                calculation_details = f"{total_days} Day(s) (Vehicle Fee + Driver Fee)"
                
            elif trip_type == 'multicity':
                # Multicity: Day-based + Extra KM charges
                # Total Vehicle Fee = Number of Days × Vehicle Fee
                # Total Driver Fee = Number of Days × Driver Fee
                # Chargeable Kilometers = Total Kilometers − (Number of Days × Vehicle Free KMs per Day)
                # Extra Kilometer Charge = Chargeable Kilometers × Fare per KM
                # Total Amount = Total Vehicle Fee + Total Driver Fee + Extra Kilometer Charge
                vehicle_fee = total_days * float(vehicle.per_day_fee)
                driver_charge = total_days * float(vehicle.driver_charge_per_day)
                free_km_total = total_days * vehicle.min_km_per_day
                chargeable_km = max(0, total_distance - free_km_total)
                extra_km_charge = chargeable_km * float(vehicle.fare_per_km)
                total_amount = vehicle_fee + driver_charge + extra_km_charge
                
                if chargeable_km > 0:
                    calculation_details = f"{total_days} Day(s) + {chargeable_km:.0f} Extra KM"
                else:
                    calculation_details = f"{total_days} Day(s) + No Extra KM"
                
            else:
                # Other trip types: Distance-based calculation
                min_distance = vehicle.min_km_per_day * total_days
                actual_distance = max(total_distance, min_distance)
                distance_charge = actual_distance * float(vehicle.fare_per_km)
                driver_charge = total_days * float(vehicle.driver_charge_per_day)
                vehicle_day_charge = total_days * float(vehicle.per_day_fee)
                total_amount = distance_charge + driver_charge + vehicle_day_charge
                calculation_details = f"{actual_distance:.0f} KM + {total_days} Day(s)"
            
            # Add calculated fields to vehicle data
            vehicle_data['total_amount'] = round(total_amount, 2)
            vehicle_data['calculation_details'] = calculation_details
            results.append(vehicle_data)
        
        # Sort by total amount
        results.sort(key=lambda x: x['total_amount'])
        
        return Response({
            'count': len(results),
            'next': None,
            'previous': None,
            'results': results
        })

