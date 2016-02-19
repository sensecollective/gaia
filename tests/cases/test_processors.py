import json
import os
import unittest
from zipfile import ZipFile

from gaia import formats

from gaia.inputs import RasterFileIO, VectorFileIO
import gaia.processes


testfile_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../data/geoprocess')


class TestGaiaProcessors(unittest.TestCase):

    def test_within(self):
        """
        Test WithinProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        process = gaia.processes.WithinProcess(inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            self.assertEquals(len(process.output.data), 19)
        finally:
            if process:
                process.purge()

    def test_intersect(self):
        """
        Test IntersectsProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_roads.geojson'))
        process = gaia.processes.IntersectsProcess(
            inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'intersects_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(format=formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_union(self):
        """
        Test UnionProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals.geojson'))
        process = gaia.processes.UnionProcess(inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'union_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(format=formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_difference(self):
        """
        Test DifferenceProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_roads.geojson'))
        process = gaia.processes.DifferenceProcess(
            inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'difference_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(format=formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_centroid(self):
        """
        Test CentroidProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        process = gaia.processes.CentroidProcess(inputs=[vector1_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'centroid_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(format=formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_distance(self):
        """
        Test DistanceProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals.geojson'))
        process = gaia.processes.DistanceProcess(
            inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'distance_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(format=formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_subset_raster(self):
        """
        Test SubsetProcess for vector & raster inputs
        """
        zipfile = ZipFile(os.path.join(testfile_path, '2states.zip'), 'r')
        zipfile.extract('2states.geojson', testfile_path)

        vector_io = VectorFileIO(
            uri=os.path.join(testfile_path, '2states.geojson'))
        raster_io = RasterFileIO(
            uri=os.path.join(testfile_path, 'globalairtemp.tif'))
        process = gaia.processes.SubsetProcess(inputs=[vector_io, raster_io])
        try:
            process.compute()
            self.assertEquals(type(process.output.data).__name__, 'Dataset')
            self.assertTrue(os.path.exists(process.output.uri))
            self.assertIsNotNone(process.id)
            self.assertIn(process.id, process.output.uri)
        finally:
            testfile = os.path.join(testfile_path, '2states.geojson')
            if os.path.exists(testfile):
                os.remove(testfile)
            if process:
                process.purge()

    def test_rastermath_add(self):
        """
        Test adding two rasters together
        """
        raster1_io = RasterFileIO(
            name='A', uri=os.path.join(testfile_path, 'globalairtemp.tif'))
        raster2_io = RasterFileIO(
            name='B', uri=os.path.join(testfile_path, 'globalprecip.tif'))
        args = {
            'calc': 'A + B',
            'bands': [1, 1]
        }
        process = gaia.processes.RasterMathProcess(
            inputs=[raster1_io, raster2_io], args=args)
        try:
            process.compute()
            self.assertTrue(os.path.exists(process.output.uri))
            oraster, raster1, raster2 = [x.read() for x in (
                process.output, raster1_io, raster2_io)]
            # Output raster should be same dimensions as raster 1
            self.assertEquals((oraster.RasterXSize, oraster.RasterYSize),
                              (raster1.RasterXSize, raster1.RasterYSize))
            orb, r1b, r2b = [x.GetRasterBand(1)
                             for x in (oraster, raster1, raster2)]
            # Min value of output should be >= the max minimum of inputs
            self.assertGreaterEqual(orb.GetStatistics(False, True)[0],
                                    max(r1b.GetStatistics(False, True)[0],
                                    r2b.GetStatistics(False, True)[0]))

            # Max value of output >=  max(minimum)+min(maximum) of inputs
            self.assertGreaterEqual(orb.GetStatistics(False, True)[1],
                                    max(r1b.GetStatistics(False, True)[0],
                                        r2b.GetStatistics(False, True)[0]) +
                                    min(r1b.GetStatistics(False, True)[1],
                                        r2b.GetStatistics(False, True)[1]))
        finally:
            if process:
                process.purge()

    def test_rastermath_multiply_by_value(self):
        """
        Test multiplying a raster by a value,
        and specifying output type (Float32)
        """
        raster1_io = RasterFileIO(
            name='A', uri=os.path.join(testfile_path, 'globalprecip.tif'))
        args = {
            'calc': 'A * 2',
            'output_type': 'Float32'
        }
        process = gaia.processes.RasterMathProcess(
            inputs=[raster1_io, ], args=args)
        try:
            process.compute()
            self.assertTrue(os.path.exists(process.output.uri))
            oraster, raster1 = [x.read() for x in (process.output, raster1_io)]
            # Output raster should be same dimensions as raster 1
            self.assertEquals((oraster.RasterXSize, oraster.RasterYSize),
                              (raster1.RasterXSize, raster1.RasterYSize))
            orb, r1b = [x.GetRasterBand(1)for x in (oraster, raster1)]
            # Maximum value of output should be 2x the max of input raster
            self.assertEqual(orb.GetStatistics(False, True)[1],
                             r1b.GetStatistics(False, True)[1] * 2)
            # Datatype of band should be Float32 (== gdal.GDT_Float32 == 6)
            self.assertEquals(6, orb.DataType)
            self.assertEquals(1.175494351E-38, orb.GetNoDataValue())

            # Each pixel of output raster should equal 2x input raster
            # unless it is a nodata value
            ora, r1a = [x.ReadAsArray() for x in (orb, r1b)]
            for x in range(raster1.RasterXSize):
                for y in range(raster1.RasterYSize):
                    if r1a[y, x] != r1b.GetNoDataValue():
                        self.assertEquals(ora[y, x], r1a[y, x] * 2)
        finally:
            if process:
                process.purge()