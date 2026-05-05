"""
Unit tests for MockMaster
"""

import unittest
import json
import tempfile
from pathlib import Path

from mockmaster.config import ConfigParser
from mockmaster.templates import TemplateEngine, ResponseBuilder
from mockmaster.storage import ProjectStorage
from mockmaster.utils import (
    generate_random_string, generate_random_uuid, generate_random_email,
    match_path_pattern, parse_query_string, safe_json_loads, safe_json_dumps
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_generate_random_string(self):
        """Test random string generation."""
        s = generate_random_string(10)
        self.assertEqual(len(s), 10)
        self.assertTrue(s.isalnum())
    
    def test_generate_random_uuid(self):
        """Test UUID generation."""
        uuid = generate_random_uuid()
        self.assertEqual(len(uuid), 36)
        self.assertEqual(uuid.count('-'), 4)
    
    def test_generate_random_email(self):
        """Test email generation."""
        email = generate_random_email()
        self.assertIn('@', email)
        self.assertIn('.', email.split('@')[1])
    
    def test_match_path_pattern(self):
        """Test path pattern matching."""
        # Exact match
        result = match_path_pattern('/users', '/users')
        self.assertEqual(result, {})
        
        # Pattern with parameter
        result = match_path_pattern('/users/123', '/users/{id}')
        self.assertEqual(result, {'id': '123'})
        
        # Multiple parameters
        result = match_path_pattern('/users/123/posts/456', '/users/{userId}/posts/{postId}')
        self.assertEqual(result, {'userId': '123', 'postId': '456'})
        
        # No match
        result = match_path_pattern('/users', '/posts')
        self.assertIsNone(result)
    
    def test_parse_query_string(self):
        """Test query string parsing."""
        result = parse_query_string('a=1&b=2')
        self.assertEqual(result, {'a': '1', 'b': '2'})
        
        result = parse_query_string('a=1&a=2')
        self.assertEqual(result, {'a': ['1', '2']})
        
        result = parse_query_string('')
        self.assertEqual(result, {})
    
    def test_safe_json_loads(self):
        """Test safe JSON loading."""
        result = safe_json_loads('{"a": 1}')
        self.assertEqual(result, {'a': 1})
        
        result = safe_json_loads('invalid json')
        self.assertEqual(result, 'invalid json')
    
    def test_safe_json_dumps(self):
        """Test safe JSON dumping."""
        result = safe_json_dumps({'a': 1})
        self.assertEqual(json.loads(result), {'a': 1})


class TestTemplateEngine(unittest.TestCase):
    """Test template engine."""
    
    def setUp(self):
        self.engine = TemplateEngine()
    
    def test_simple_variable(self):
        """Test simple variable substitution."""
        result = self.engine.render("Hello {{ name }}", {'name': 'World'})
        self.assertEqual(result, "Hello World")
    
    def test_random_generators(self):
        """Test random data generators."""
        result = self.engine.render("{{ random_string(8) }}", {})
        self.assertEqual(len(result), 8)
        
        result = self.engine.render("{{ random_uuid() }}", {})
        self.assertEqual(len(result), 36)
    
    def test_nested_render(self):
        """Test rendering nested structures."""
        template = {
            'name': '{{ name }}',
            'id': '{{ random_uuid() }}'
        }
        result = self.engine.render(template, {'name': 'Test'})
        self.assertEqual(result['name'], 'Test')
        self.assertEqual(len(result['id']), 36)


class TestResponseBuilder(unittest.TestCase):
    """Test response builder."""
    
    def setUp(self):
        self.builder = ResponseBuilder()
    
    def test_build_simple_response(self):
        """Test building simple response."""
        config = {
            'status': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': {'message': 'OK'}
        }
        response = self.builder.build_response(config)
        
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['headers']['Content-Type'], 'application/json')
        self.assertIn('message', json.loads(response['body']))
    
    def test_build_response_with_params(self):
        """Test building response with path parameters."""
        config = {
            'status': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': {'id': '{{ id }}'}
        }
        response = self.builder.build_response(config, path_params={'id': '123'})
        
        body = json.loads(response['body'])
        self.assertEqual(body['id'], '123')
    
    def test_build_error_response(self):
        """Test building error response."""
        response = self.builder.build_error_response(
            status=404,
            message="Not Found"
        )
        
        self.assertEqual(response['status'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['error']['message'], "Not Found")


class TestConfigParser(unittest.TestCase):
    """Test configuration parser."""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / 'test.json'
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_parse_simple_json(self):
        """Test parsing simple JSON."""
        config = {
            'server': {'port': 8080, 'host': 'localhost'},
            'routes': [
                {'path': '/', 'methods': ['GET'], 'response': {'status': 200}}
            ]
        }
        self.config_path.write_text(json.dumps(config))
        parser = ConfigParser(str(self.config_path))
        
        self.assertEqual(parser.get_port(), 8080)
        self.assertEqual(parser.get_host(), 'localhost')
        self.assertEqual(len(parser.get_routes()), 1)
    
    def test_find_route(self):
        """Test finding routes."""
        config = {
            'routes': [
                {'path': '/users', 'methods': ['GET'], 'response': {'status': 200}},
                {'path': '/users/{id}', 'methods': ['GET'], 'response': {'status': 200}}
            ]
        }
        self.config_path.write_text(json.dumps(config))
        parser = ConfigParser(str(self.config_path))
        
        route = parser.find_route('GET', '/users')
        self.assertIsNotNone(route)
        
        route = parser.find_route('GET', '/users/123')
        self.assertIsNotNone(route)
        self.assertEqual(route['_path_params'], {'id': '123'})
    
    def test_validate_config(self):
        """Test configuration validation."""
        config = {
            'routes': [
                {'path': '/', 'methods': ['GET'], 'response': {'status': 200}}
            ]
        }
        self.config_path.write_text(json.dumps(config))
        parser = ConfigParser(str(self.config_path))
        
        errors = parser.validate()
        self.assertEqual(len(errors), 0)
    
    def test_validate_missing_fields(self):
        """Test validation of missing fields."""
        config = {
            'routes': [
                {'path': '/'}
            ]
        }
        self.config_path.write_text(json.dumps(config))
        parser = ConfigParser(str(self.config_path))
        
        errors = parser.validate()
        self.assertTrue(len(errors) > 0)


class TestProjectStorage(unittest.TestCase):
    """Test project storage."""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = ProjectStorage(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_create_project(self):
        """Test creating a project."""
        config_path = Path(self.temp_dir.name) / 'test.json'
        config_path.write_text('{"routes": []}')
        
        project = self.storage.create_project(
            name='test-project',
            config_path=str(config_path),
            description='Test project'
        )
        
        self.assertEqual(project['name'], 'test-project')
        self.assertEqual(project['description'], 'Test project')
    
    def test_get_project(self):
        """Test getting a project."""
        config_path = Path(self.temp_dir.name) / 'test.json'
        config_path.write_text('{"routes": []}')
        
        self.storage.create_project(
            name='test-project',
            config_path=str(config_path)
        )
        
        project = self.storage.get_project('test-project')
        self.assertIsNotNone(project)
        self.assertEqual(project['name'], 'test-project')
        
        project = self.storage.get_project('non-existent')
        self.assertIsNone(project)
    
    def test_list_projects(self):
        """Test listing projects."""
        config_path = Path(self.temp_dir.name) / 'test.json'
        config_path.write_text('{"routes": []}')
        
        self.storage.create_project(
            name='project-1',
            config_path=str(config_path)
        )
        self.storage.create_project(
            name='project-2',
            config_path=str(config_path)
        )
        
        projects = self.storage.list_projects()
        self.assertEqual(len(projects), 2)
    
    def test_delete_project(self):
        """Test deleting a project."""
        config_path = Path(self.temp_dir.name) / 'test.json'
        config_path.write_text('{"routes": []}')
        
        self.storage.create_project(
            name='test-project',
            config_path=str(config_path)
        )
        
        result = self.storage.delete_project('test-project')
        self.assertTrue(result)
        
        result = self.storage.delete_project('non-existent')
        self.assertFalse(result)
    
    def test_duplicate_project(self):
        """Test duplicating a project."""
        config_path = Path(self.temp_dir.name) / 'test.json'
        config_path.write_text('{"routes": []}')
        
        self.storage.create_project(
            name='original',
            config_path=str(config_path)
        )
        
        duplicated = self.storage.duplicate_project('original', 'copy')
        self.assertIsNotNone(duplicated)
        self.assertEqual(duplicated['name'], 'copy')


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_workflow(self):
        """Test complete workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config
            config_path = Path(temp_dir) / 'api.json'
            config = {
                'server': {'port': 9999, 'host': 'localhost'},
                'routes': [
                    {
                        'path': '/api/users',
                        'methods': ['GET'],
                        'response': {
                            'status': 200,
                            'headers': {'Content-Type': 'application/json'},
                            'body': {'users': [], 'total': 0}
                        }
                    }
                ]
            }
            config_path.write_text(json.dumps(config))
            
            # Parse config
            parser = ConfigParser(str(config_path))
            self.assertEqual(parser.get_port(), 9999)
            
            # Find route
            route = parser.find_route('GET', '/api/users')
            self.assertIsNotNone(route)
            
            # Build response
            builder = ResponseBuilder()
            response = builder.build_response(route.get('response', {'status': 200}))
            self.assertEqual(response['status'], 200)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigParser))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())