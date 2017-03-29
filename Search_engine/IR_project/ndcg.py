import math

# compute NDCG ranking
def computeNDCG(ranking_score):
	ranking_score_new = []
	ranking_score_final =[]
	ranking_score_new.append(ranking_score[0])
	ranking_score_final.append(ranking_score[0])
	
	for i in range(1, len(ranking_score)):
		ranking_score_new.append(ranking_score[i]/ math.log(i+1,2))
		
	for i in range(1, len(ranking_score)):
		sum =0
		for j in range(0,i+1):
			sum = sum + ranking_score_new[j]
		ranking_score_final.append(sum)
	return ranking_score_final
	

# compare NDCG ranking for actual vs ideal
def compareNDCG(actual_ranking, ideal_ranking):
	final_ndcg =[]
	for i in range(0, len(actual_ranking)):
		final_ndcg.append(actual_ranking[i] / ideal_ranking[i])
	return final_ndcg
	
ideal=[5,5,5,4,4,3,3,2,1,0]

actual=[0,0,5,5,0,4,0,0,0,0]

actual_ranking_score	= computeNDCG(actual)
ideal_ranking_score = computeNDCG(ideal)
print "actual",actual_ranking_score
print "ideal",ideal_ranking_score
final_score= compareNDCG(actual_ranking_score,ideal_ranking_score)
print "final score",final_score
