import pickle
def ModelIt(y_true, features = []):
	f = open('/home/maksat/Desktop/Insight/app/simple_clasifier.pickle', 'rb')
	clf = pickle.load(f)
	f.close()

	#print(dir(clf))
	#return clf.feature_importances_[0]
	result = clf.predict(features)

	
	return {'true':y_true, 'predict':result[0]}
