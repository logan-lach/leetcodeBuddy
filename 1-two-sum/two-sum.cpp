class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        
        unordered_map<int,int> holder;
        
        for (int i = 0; i < nums.size(); i ++)
        {
            auto res = holder.find(target - nums[i]);
            if (res != holder.end())
            {
                return vector<int>{res->second, i};
            }
            else
            {
                holder[nums[i]] = i;
            }
        }

        return {-1, -1};
    }
};