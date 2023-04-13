import pytest
import os
from dotenv import load_dotenv
from tests.my_helper_functions import (
    my_get_folder_ids,
    my_get_subset_ids,
    my_get_version_ids,
    my_get_representation_ids,
    my_delete_folder
)
from ayon_api.operations import (
    OperationsSession,
    new_folder_entity,
    new_subset_entity,
    new_version_entity,
    new_representation_entity
)
from ayon_api import (
    get_versions,
    get_folder_by_id,
    get_subset_by_id,
    get_folder_by_name,
    get_subset_by_name,
    get_folders,
    get_subsets,
    get_versions,
    get_representations
)
from ayon_api.exceptions import (
    FailedOperations
)


AYON_BASE_URL = "https://ayon.dev"
AYON_REST_URL = "https://ayon.dev/api"
PROJECT_NAME = "demo_Commercial"


@pytest.fixture
def folder():
    folder_name = "testingFolder"
    return new_folder_entity(folder_name, "Folder")


@pytest.mark.parametrize(
    "folder_name",
    [
        ("testfolder1"),
        ("testfolder2"),
        ("testfolder3")
    ]
)
def test_operations_with_folder(folder_name):
    folder = new_folder_entity(folder_name, "Folder")

    s = OperationsSession()
    op = s.create_entity(PROJECT_NAME, "folder", folder)
    folder_id = op.entity_id
    s.commit()

    folder_entity = get_folder_by_id(PROJECT_NAME, folder_id)
    s.update_entity(
        PROJECT_NAME,
        "folder",
        folder_entity["id"],
        {"attrib": {"frameStart": 1002}}
    )
    s.commit()
    folder_entity = get_folder_by_id(PROJECT_NAME, folder_id)
    assert folder_entity["attrib"]["frameStart"] == 1002

    my_delete_folder(s, PROJECT_NAME, folder_entity["id"])
    assert get_folder_by_id(PROJECT_NAME, folder_id) is None

"""
def test_operations_with_folder_exception(folder):
    try:
        s = OperationsSession()
        op = s.create_entity(PROJECT_NAME, "folder", folder)
        folder_id = op.entity_id
        s.commit()
        
        folder_entity = get_folder_by_id(PROJECT_NAME, folder_id)
        s.update_entity(
            PROJECT_NAME,
            "folder",
            folder_entity["id"],
            {"attrib": {"xyz": 1002}}
        )
        s.commit()

        folder_entity = get_folder_by_id(PROJECT_NAME, folder_id)

        # Test that wrong attribute is not there
        with pytest.raises(KeyError):
            assert folder_entity["attrib"]["xyz"] == 1002

    finally:
        my_delete_folder(s, PROJECT_NAME, folder_entity["id"])
        assert get_folder_by_id(PROJECT_NAME, folder_id) is None
"""


@pytest.mark.parametrize(
    "folder_name",
    [
        ("!invalid"),
        ("in/valid"),
        ("in~valid")
    ]
)
def test_folder_name_invalid_characters(folder_name):
    """in-valid is OK
    """

    s = OperationsSession()

    with pytest.raises(KeyError):
        folder = new_folder_entity(folder_name, "Folder")
        op = s.create_entity(PROJECT_NAME, "folder", folder)
        s.commit()


@pytest.mark.parametrize(
    "folder_name",
    [
        ("test_folder1"),
    ]
)
def test_folder_duplicated_names(folder_name):
    s = OperationsSession()

    folder = new_folder_entity(folder_name, "Folder")
    op = s.create_entity(PROJECT_NAME, "folder", folder)
    folder_id = op.entity_id
    s.commit()

    with pytest.raises(FailedOperations):
        folder = new_folder_entity(folder_name, "Folder")
        op = s.create_entity(PROJECT_NAME, "folder", folder)
        s.commit()

    folder_entity = get_folder_by_id(PROJECT_NAME, folder_id)
    my_delete_folder(s, PROJECT_NAME, folder_entity["id"])
    assert get_folder_by_id(PROJECT_NAME, folder_id) is None


@pytest.mark.parametrize(
    "folder_name, subset_names",
    [
        ("test_folder6", ["modelMain", "modelProxy", "modelSculpt"]),
    ]
)
def test_subset_duplicated_names(folder_name, subset_names):
    s = OperationsSession()

    folder = new_folder_entity(folder_name, "Folder")
    op = s.create_entity(PROJECT_NAME, "folder", folder)
    folder_id = op.entity_id
    s.commit()

    subset_ids = []
    for name in subset_names:
        subset = new_subset_entity(name, "model", folder_id)
        op = s.create_entity(PROJECT_NAME, "subset", subset)    
        s.commit()
        subset_ids.append(op.entity_id)

    for name in subset_names:
        with pytest.raises(FailedOperations):
            subset = new_subset_entity(name, "model", folder_id)
            _ = s.create_entity(PROJECT_NAME, "subset", subset)    
            s.commit()

    for subset_id in subset_ids:
        s.delete_entity(PROJECT_NAME, "subset", subset_id)
        s.commit()
        assert get_subset_by_id(PROJECT_NAME, subset_id) is None

    s.delete_entity(name, "folder", folder_id)
    s.commit()
    assert get_folder_by_id(PROJECT_NAME, folder_id) is None

@pytest.mark.parametrize(
    "folder_name, subset_name, version_name, representation_name",
    [
        ("testFolder1", "modelMain", "version1", "representation1"),
        ("testFolder2", "modelMain", "version2", "representation2"),
        ("testFolder3", "modelMain", "version3", "representation3")
    ]
)
def test_hierarchy_folder_subset_version_repre(
    folder_name, 
    subset_name, 
    version_name, 
    representation_name
):
    s = OperationsSession()

    folder = new_folder_entity(folder_name, "Folder")
    op = s.create_entity(PROJECT_NAME, "folder", folder)    
    folder_id = op.entity_id
    s.commit()
    
    subset = new_subset_entity(subset_name, "model", folder_id)
    op = s.create_entity(PROJECT_NAME, "subset", subset)    
    subset_id = op.entity_id
    s.commit()

    version = new_version_entity(1, subset_id)
    op = s.create_entity(PROJECT_NAME, "version", version)   
    version_id = op.entity_id
    s.commit()

    res = get_subsets(PROJECT_NAME, folder_ids=set(folder_id))

    s.delete_entity(PROJECT_NAME, "subset", subset_id)
    s.commit()

    s.delete_entity(PROJECT_NAME, "folder", folder_id)
    s.commit()


@pytest.mark.parametrize(
    "folder_name, subset_name, version_name, representation_name, num_of_versions",
    [
        # ("testFolder1", "modelMain", "version", "representation", 3),
        # ("testFolder2", "modelMain", "version", "representation"),
        ("testFolder4", "modelMain", "version", "representation", 2)
    ]
)
def test_large_folder(
    folder_name, 
    subset_name, 
    version_name, 
    representation_name,
    num_of_versions
):
    """Creates the whole hierarchy (folder, subset, version, representation).
    Tries to create versions and representations with duplicated 
    names and checks if exceptions are raised.
    
    """

    s = OperationsSession()

    # create folder
    folder = new_folder_entity(folder_name, "Folder")
    op = s.create_entity(PROJECT_NAME, "folder", folder)    
    folder_id = op.entity_id
    s.commit()

    s_folder_ids = my_get_folder_ids()
    assert folder_id in s_folder_ids

    # create subset
    subset = new_subset_entity(subset_name, "model", folder_id)
    op = s.create_entity(PROJECT_NAME, "subset", subset)    
    subset_id = op.entity_id
    s.commit()

    s_subset_ids = my_get_subset_ids([folder_id])
    assert subset_id in s_subset_ids

    # create versions
    my_version_ids = []
    for i in range(num_of_versions):
        version = new_version_entity(i, subset_id)
        version_id = s.create_entity(PROJECT_NAME, "version", version)["id"]   
        s.commit()

        my_version_ids.append(version_id)        

        # test duplicate name
        with pytest.raises(FailedOperations):
            version = new_version_entity(i, subset_id)
            op = s.create_entity(PROJECT_NAME, "version", version)   
            s.commit()
        
        # check if everything is created
        s_version_ids = my_get_version_ids(subset_id)
        assert len(my_version_ids) == len(s_version_ids)
        assert version_id in s_version_ids

    # create representations
    for i, version_id in enumerate(my_version_ids):
        for j in range(3):
            unique_name = str(i) + "v" + str(j)  # unique in this version
            representation = new_representation_entity(unique_name, version_id)
            representation_id = s.create_entity(PROJECT_NAME, "representation", representation)["id"]
            s.commit()
            
            server_representations = my_get_representation_ids([version_id])
            assert representation_id in server_representations
            
            # not fixed on server yet
            """
            # not unique under this version
            with pytest.raises(FailedOperations):
                representation = new_representation_entity(unique_name, version_id)
                _ = s.create_entity(PROJECT_NAME, "representation", representation)  
                s.commit()
            """

            # under different version will be created
            if i > 0:
                representation = new_representation_entity(unique_name, my_version_ids[i-1])
                representation_id = s.create_entity(PROJECT_NAME, "representation", representation)["id"]
                s.commit()

                s_representation_ids = my_get_representation_ids(my_version_ids)
                assert representation_id in s_representation_ids
    
    s.delete_entity(PROJECT_NAME, "subset", subset_id)
    s.commit()

    s.delete_entity(PROJECT_NAME, "folder", folder_id)
    s.commit()



"""
def test_large_project_hierarchy():
    s = OperationsSession()
    folders = []

    folder_name = "testFolder"

    try:
        # create folders
        for num in range(3):
            name = folder_name + str(num)
            folder = new_folder_entity(name, "Folder")
            op = s.create_entity(PROJECT_NAME, "folder", folder)
            folders.append(
            {
                "name": name,
                "id": op.entity_id,
            }
            )
            s.commit()

        # create subsets in all folders
        subset_prep = [
            ("modelMain", "model"), 
            ("modelProxy", "model"),
            ("modelSculpt", "model")
        ]
        for i, (name, family) in enumerate(subset_prep):
            subset = new_subset_entity(name, family, folders[i]["id"])
            op = s.create_entity(PROJECT_NAME, "subset", subset)
            subset_id = op.entity_id
            s.commit()

    finally:
        # delete folders
        for folder in folders:
            folder_entity = get_folder_by_id(PROJECT_NAME, folder["id"])
            my_delete_folder(s, PROJECT_NAME, folder_entity["id"])
"""

@pytest.mark.parametrize(
    "folder_name",
    [
        ("testfolder1"),
        ("testFolder1"),
        ("testfolder1_1"),
        ("testFolder2")
    ]
)
def test_delete_folder_with_subset(folder_name):
    s = OperationsSession()

    folder_entity = get_folder_by_name(PROJECT_NAME, folder_name)

    my_delete_folder(s, PROJECT_NAME, folder_entity["id"])
    s.commit()


@pytest.mark.parametrize(
    "folder_name",
    [
        ("test_folder0"),
        ("test_folder1"),
        ("test_folder2"),
        ("test_folder3"),
        ("test_folder5"),
        ("test_folder6"),
    ]
)
def test_manual_delete_hierarchy(folder_name):
    s = OperationsSession()

    folder_id = get_folder_by_name(PROJECT_NAME, folder_name)["id"]
    subset_ids = my_get_subset_ids([folder_id])

    for subset_id in subset_ids:
        s.delete_entity(PROJECT_NAME, "subset", subset_id)
        s.commit()

    s.delete_entity(PROJECT_NAME, "folder", folder_id)
    s.commit()
