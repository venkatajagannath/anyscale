import json

from anyscale.aws_iam_policies import ANYSCALE_IAM_POLICIES


def test_policy_sid_unique():
    """
    Please do not change this test.

    This test is to ensure
    1) The policy version is 2012-10-17
    2) The policy statement has a Sid
    3) The Sid is unique
    """
    policy_sids = []
    for policy in ANYSCALE_IAM_POLICIES:
        policy_document = json.loads(policy.policy_document)
        assert policy_document["Version"] == "2012-10-17"
        for statement in policy_document["Statement"]:
            assert "Sid" in statement
            policy_sids.append(statement["Sid"])
    assert len(policy_sids) == len(set(policy_sids))
