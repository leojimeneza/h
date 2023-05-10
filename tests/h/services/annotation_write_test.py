from unittest.mock import Mock, patch, sentinel

import pytest
from h_matchers import Any

from h.models import Annotation
from h.schemas import ValidationError
from h.security import Permission
from h.services.annotation_write import AnnotationWriteService, service_factory
from h.traversal.group import GroupContext


class TestAnnotationWriteService:
    def test_create_annotation(
        self,
        svc,
        create_data,
        factories,
        update_document_metadata,
        search_index,
        annotation_read_service,
        _validate_group,
    ):
        root_annotation = factories.Annotation()
        annotation_read_service.get_annotation_by_id.return_value = root_annotation
        create_data["references"] = [root_annotation.id, factories.Annotation().id]
        create_data["groupid"] = "IGNORED"
        update_document_metadata.return_value = factories.Document()

        result = svc.create_annotation(create_data)

        annotation_read_service.get_annotation_by_id.assert_called_once_with(
            root_annotation.id
        )
        _validate_group.assert_called_once_with(result)
        # pylint: disable=protected-access
        search_index._queue.add_by_id.assert_called_once_with(
            result.id, tag="storage.create_annotation", schedule_in=60
        )

        assert result == Any.instance_of(Annotation).with_attrs(
            {
                "userid": create_data["userid"],
                "groupid": root_annotation.groupid,
                "target_uri": create_data["target_uri"],
                "references": create_data["references"],
                "document": update_document_metadata.return_value,
            }
        )

    def test_create_annotation_as_root(
        self, svc, create_data, factories, annotation_read_service
    ):
        group = factories.Group()
        create_data["references"] = None
        create_data["groupid"] = group.pubid

        result = svc.create_annotation(create_data)

        annotation_read_service.get_annotation_by_id.assert_not_called()
        assert result.groupid == group.pubid

    def test_create_annotation_with_invalid_parent(
        self, svc, create_data, annotation_read_service
    ):
        create_data["references"] = ["NOPE!"]
        annotation_read_service.get_annotation_by_id.return_value = None

        with pytest.raises(ValidationError):
            svc.create_annotation(create_data)

    def test__validate_group_with_no_group(self, svc, annotation):
        annotation.group = None

        with pytest.raises(ValidationError):
            svc._validate_group(annotation)  # pylint: disable=protected-access

    def test__validate_group_with_no_permission(self, svc, annotation, has_permission):
        has_permission.return_value = False

        with pytest.raises(ValidationError):
            svc._validate_group(annotation)  # pylint: disable=protected-access

        has_permission.assert_called_once_with(
            Permission.Group.WRITE, context=GroupContext(annotation.group)
        )

    @pytest.mark.parametrize("enforce_scope", (True, False))
    @pytest.mark.parametrize("matching_scope", (True, False))
    @pytest.mark.parametrize("has_scopes", (True, False))
    def test__validate_group_with_url_not_in_scopes(
        self, svc, annotation, factories, enforce_scope, matching_scope, has_scopes
    ):
        annotation.group.enforce_scope = enforce_scope
        annotation.target_uri = "http://scope" if matching_scope else "http://MISMATCH"
        if has_scopes:
            annotation.group.scopes = [factories.GroupScope(scope="http://scope")]

        if enforce_scope and has_scopes and not matching_scope:
            with pytest.raises(ValidationError):
                svc._validate_group(annotation)  # pylint: disable=protected-access
        else:
            svc._validate_group(annotation)  # pylint: disable=protected-access

    @pytest.fixture
    def create_data(self, factories):
        user = factories.User()

        return {
            "userid": user.userid,
            "target_uri": "http://example.com/target",
            "document": {
                "document_uri_dicts": sentinel.uri_dicts,
                "document_meta_dicts": sentinel.document_dicts,
            },
        }

    @pytest.fixture
    def annotation(self, factories):
        return factories.Annotation()

    @pytest.fixture
    def has_permission(self):
        return Mock(return_value=True)

    @pytest.fixture
    def svc(self, db_session, has_permission, search_index, annotation_read_service):
        return AnnotationWriteService(
            db_session=db_session,
            has_permission=has_permission,
            search_index_service=search_index,
            annotation_read_service=annotation_read_service,
        )

    @pytest.fixture
    def _validate_group(self, svc):
        with patch.object(svc, "_validate_group") as _validate_group:
            yield _validate_group

    @pytest.fixture(autouse=True)
    def update_document_metadata(self, patch, factories):
        update_document_metadata = patch(
            "h.services.annotation_write.update_document_metadata"
        )
        update_document_metadata.return_value = factories.Document()
        return update_document_metadata


class TestServiceFactory:
    def test_it(
        self,
        pyramid_request,
        AnnotationWriteService,
        search_index,
        annotation_read_service,
    ):
        svc = service_factory(sentinel.context, pyramid_request)

        AnnotationWriteService.assert_called_once_with(
            db_session=pyramid_request.db,
            has_permission=pyramid_request.has_permission,
            search_index_service=search_index,
            annotation_read_service=annotation_read_service,
        )
        assert svc == AnnotationWriteService.return_value

    @pytest.fixture
    def AnnotationWriteService(self, patch):
        return patch("h.services.annotation_write.AnnotationWriteService")