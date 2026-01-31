from typing import Protocol, TypeVar, List, Optional

T = TypeVar('T')

class MyDBPort(Protocol[T]):

    def add(self, entity: T) -> T:
        """새 엔티티 추가"""
        ...

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """ID로 엔티티 조회"""
        ...

    def get_all(self) -> List[T]:
        """모든 엔티티 조회"""
        ...

    def filter_by(self, **kwargs) -> List[T]:
        """조건으로 필터링"""
        ...

    def update(self, entity: T) -> T:
        """엔티티 업데이트"""
        ...

    def delete(self, entity: T) -> None:
        """엔티티 삭제"""
        ...

    def commit(self) -> None:
        """트랜잭션 커밋"""
        ...

    def rollback(self) -> None:
        """트랜잭션 롤백"""
        ...