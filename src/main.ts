import './style.css';
import { mountEstimator } from './estimator';
import { setupNav } from './nav';

setupNav(document);

const estimatorRoot = document.getElementById('estimator-root');
if (estimatorRoot) mountEstimator(estimatorRoot);
