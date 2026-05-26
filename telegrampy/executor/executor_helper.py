import importlib.util
import inspect
import logging
import os
from pathlib import Path
from typing import Any, Optional, List, Union, Tuple, Iterator

from telegrampy.constants.file_constants import DEFAULT_TASKS_FOLDER
from telegrampy.models.telegram_task import TelegramTask
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.util.log_util import getlogger

logger = getlogger(__name__, logging.WARN)


class ExecutorHelper:
    @staticmethod
    def load_task(task_name: str, telegram_py_app: TelegramPyApp) -> Any:

        abs_paths = ExecutorHelper.build_search_paths(path=DEFAULT_TASKS_FOLDER)

        task: TelegramTask | Any = ExecutorHelper._load_object(paths=abs_paths,
                                                               object_name=task_name,
                                                               add_source=True,
                                                               kwargs={},
                                                               )
        if task is None:
            logger.error(f"Unable to load task with name \"{task_name}\"")
        else:
            if isinstance(task, TelegramTask):
                task.set_telegram_py_app(telegram_py_app)
                pass
            pass

        return task

    @classmethod
    def build_search_paths(cls, path) -> List[Path]:

        abs_paths: List[Path] = []
        subdirectories = []
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                subdirectories.append(Path(os.path.join(root, dir)))
        abs_paths.append(Path(path))
        abs_paths.extend(subdirectories)
        return abs_paths

    @classmethod
    def _load_object(cls, paths: List[Path], object_name: str, add_source: bool = False,
                     kwargs: dict = {}) -> Optional[Any]:
        """
        Try to load object from path list.
        """

        for _path in paths:
            try:
                (module, module_path) = cls._search_object(directory=_path,
                                                           object_name=object_name,
                                                           add_source=add_source)
                if module:
                    logger.info(
                        f"Using resolved  {object_name} "
                        f"from '{module_path}'...")
                    return module(**kwargs)
            except FileNotFoundError:
                logger.warning('Path "%s" does not exist.', _path.resolve())
            except Exception as e:
                logger.exception(e)
        return None

    @classmethod
    def _search_object(cls, directory: Path, *, object_name: str, add_source: bool = False
                       ) -> Union[Tuple[Any, Path], Tuple[None, None]]:
        logger.debug(f"Searching for {object_name} in '{directory}'")
        for entry in directory.iterdir():
            # Only consider python files
            if not str(entry).endswith('.py'):
                logger.debug('Ignoring %s', entry)
                continue
            if entry.is_symlink() and not entry.is_file():
                logger.debug('Ignoring broken symlink %s', entry)
                continue
            module_path = entry.resolve()

            obj = next(cls._get_valid_object(module_path, object_name), None)

            if obj:
                obj[0].__file__ = str(entry)
                if add_source:
                    obj[0].__source__ = obj[1]
                return (obj[0], module_path)
        return (None, None)

    @classmethod
    def _get_valid_object(cls, module_path: Path, object_name: Optional[str],
                          enum_failed: bool = False) -> Iterator[Any]:

        # Generate spec based on absolute path
        # Pass object_name as first argument to have logging print a reasonable name.
        spec = importlib.util.spec_from_file_location(object_name or "", str(module_path))
        if not spec:
            return iter([None])

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore # importlib does not use typehints
        except (ModuleNotFoundError, SyntaxError, ImportError, NameError) as err:
            # Catch errors in case a specific module is not installed
            logger.warning(f"Could not import {module_path} due to '{err}'")
            if enum_failed:
                return iter([None])
        valid_objects_gen = (
            (obj, inspect.getsource(module))
            for name, obj in inspect.getmembers(module, inspect.isclass) if
            (object_name is None or object_name == name))
        return valid_objects_gen
