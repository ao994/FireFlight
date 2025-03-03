#Everyone

from django.test import TestCase
from .models import Species, Grid, Results


# Create your tests here.
class AddingDataTests(TestCase):
    def setUp(self):
        Species.objects.create(speciesID=0, species="Fake Bird", birdcode="BIRDCODE")
        
        Grid.objects.create(OID=1, Grid_ID="NM-CARSON-LE1", Grid_E_NAD83=388500,Grid_N_NAD83=4091500,UTM_Zone=13,Grid_Lat_NAD83=36.96299337,Grid_Long_NAD83=-106.2525113,BCR=16,MgmtEntity="US Forest Service", MgmtRegion="USFS Region 3",MgmtUnit="Carson National Forest",MgmtDistrict="Tres Piedras Ranger District",County="Rio Arriba",State="NM",PriorityLandscape="Enchanted Circle",inPL=0)

        Results.objects.create(bird_speciesID=0, gridID= 0, lbci= 1.1, posterior_median= 2.2, ubci=3.3)
    
    
    def test_adding_bird_and_result_only(self):
        """
        checks that the bird and result were added correctly to the database.
        """
        
        